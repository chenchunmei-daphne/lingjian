"""Capability-centred dense retrieval for the v02 knowledge base."""

from __future__ import annotations

import re
from typing import Dict, List

import chromadb
from sentence_transformers import SentenceTransformer

from schemas import QueryIntent, SearchResult
from vector_kb_v02 import (
    DEFAULT_COLLECTION,
    DEFAULT_DATA_FILE,
    DEFAULT_DB_DIR,
    DEFAULT_MODEL_DIR,
    load_dataset,
)


TOKEN_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*|[\u4e00-\u9fff]{2,}")


class FealpyRetriever:
    """Retrieve capabilities and expose their target interfaces to callers."""

    def __init__(
        self,
        model_path=DEFAULT_MODEL_DIR,
        db_path=DEFAULT_DB_DIR,
        data_path=DEFAULT_DATA_FILE,
        collection_name: str = DEFAULT_COLLECTION,
    ) -> None:
        self.model = SentenceTransformer(str(model_path))
        client = chromadb.PersistentClient(path=str(db_path))
        self.collection = client.get_collection(collection_name)
        data = load_dataset(data_path)
        self.schema_version = data["schema_version"]
        self.dataset_version = data["dataset_version"]
        self.records: Dict[str, dict] = {
            record["id"]: record for record in data["interfaces"]
        }
        self.capabilities: Dict[str, dict] = {
            capability["id"]: capability for capability in data["capabilities"]
        }

    @staticmethod
    def _query_text(intent: QueryIntent) -> str:
        """Keep the user's wording dominant for capability retrieval."""
        parts = [intent.original_query]
        if intent.interface_hints:
            parts.append("接口提示：" + "、".join(intent.interface_hints))
        return "\n".join(parts)

    @staticmethod
    def _lexical_bonus(intent: QueryIntent, capability: dict) -> float:
        query = intent.original_query.lower()
        targets = capability.get("target_interfaces") or []
        target_ids = [item.get("id", "").lower() for item in targets]
        bonus = 0.0
        for hint in intent.interface_hints:
            normalized = hint.lower().removeprefix("bm.")
            if any(
                target.removeprefix("bm.") == normalized
                or target.endswith("." + normalized)
                for target in target_ids
            ):
                bonus += 0.35
            elif any(
                normalized.split(".")[-1] == target.split(".")[-1]
                for target in target_ids
            ):
                bonus += 0.12

        searchable = " ".join([
            capability.get("intent") or "",
            *(capability.get("expressions") or []),
            *(capability.get("tags") or []),
        ]).lower()
        tokens = TOKEN_PATTERN.findall(query)
        hits = sum(token in searchable for token in tokens if len(token) > 1)
        return bonus + min(hits * 0.02, 0.1)

    def _result_record(
        self,
        interface_id: str,
        capability: dict,
        target: dict,
    ) -> dict:
        """Add capability evidence without mutating the interface fact table."""
        record = dict(self.records[interface_id])
        record.setdefault("full_name", interface_id)
        record.setdefault(
            "description", record.get("summary") or capability["intent"]
        )
        record.update({
            "capability_id": capability["id"],
            "capability_intent": capability["intent"],
            "match_reason": target.get("reason") or capability["intent"],
            "target_role": target.get("role") or "primary",
            "contrasts": capability.get("contrasts") or [],
        })
        return record

    def search(self, intent: QueryIntent) -> List[SearchResult]:
        query_embedding = self.model.encode(
            [self._query_text(intent)], normalize_embeddings=True
        ).tolist()
        candidate_count = min(max(intent.top_k * 6, 20), self.collection.count())
        response = self.collection.query(
            query_embeddings=query_embedding,
            n_results=candidate_count,
            include=["distances"],
        )

        by_interface: Dict[str, SearchResult] = {}
        for capability_id, distance in zip(
            response["ids"][0], response["distances"][0]
        ):
            capability = self.capabilities.get(capability_id)
            if not capability:
                continue
            base_score = (
                1.0 - float(distance)
                + self._lexical_bonus(intent, capability)
            )
            for target in capability.get("target_interfaces") or []:
                interface_id = target.get("id")
                record = self.records.get(interface_id)
                if not record:
                    continue
                score = base_score
                if target.get("role") != "primary":
                    score -= 0.01
                if intent.category == record.get("category"):
                    score += 0.08
                result = SearchResult(
                    id=interface_id,
                    score=score,
                    distance=float(distance),
                    record=self._result_record(
                        interface_id, capability, target
                    ),
                )
                previous = by_interface.get(interface_id)
                if previous is None or result.score > previous.score:
                    by_interface[interface_id] = result

        results = sorted(
            by_interface.values(), key=lambda item: item.score, reverse=True
        )
        return results[:intent.top_k]
