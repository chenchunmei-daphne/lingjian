"""Dense retrieval plus deterministic filtering and re-ranking."""

from __future__ import annotations

from typing import Dict, List, Optional

import chromadb
from sentence_transformers import SentenceTransformer

from schemas import QueryIntent, SearchResult
from vector_kb import (
    DEFAULT_COLLECTION,
    DEFAULT_DATA_FILE,
    DEFAULT_DB_DIR,
    DEFAULT_MODEL_DIR,
    load_interfaces,
)


class FealpyRetriever:
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
        self.records: Dict[str, dict] = {
            record["id"]: record for record in load_interfaces(data_path)
        }

    @staticmethod
    def _query_text(intent: QueryIntent) -> str:
        parts = [intent.original_query, f"操作：{intent.operation}"]
        if intent.category:
            parts.append(f"分类：{intent.category}")
        if intent.backend:
            parts.append(f"后端：{intent.backend}")
        if intent.parameters:
            parts.append(f"参数：{intent.parameters}")
        return "\n".join(parts)

    @staticmethod
    def _lexical_bonus(intent: QueryIntent, record: dict) -> float:
        query = intent.original_query.lower()
        name = record["full_name"].lower()
        bonus = 0.0
        for hint in intent.interface_hints:
            if name == f"bm.{hint}" or name.endswith(f".{hint}"):
                bonus += 0.35
            elif hint.split(".")[-1] in name:
                bonus += 0.12
        searchable = " ".join(
            [record.get("description") or ""]
            + list(record.get("aliases") or [])
            + list(record.get("keywords") or [])
        ).lower()
        hits = sum(token in searchable for token in query.split() if len(token) > 1)
        return bonus + min(hits * 0.02, 0.1)

    def search(self, intent: QueryIntent) -> List[SearchResult]:
        query_embedding = self.model.encode(
            [self._query_text(intent)], normalize_embeddings=True
        ).tolist()
        candidate_count = min(max(intent.top_k * 6, 20), self.collection.count())
        where = {"category": intent.category} if intent.category else None
        response = self.collection.query(
            query_embeddings=query_embedding,
            n_results=candidate_count,
            where=where,
            include=["distances"],
        )

        results = []
        for item_id, distance in zip(response["ids"][0], response["distances"][0]):
            record = self.records.get(item_id)
            if not record:
                continue
            if intent.backend:
                backend_api = (
                    record.get("backends", {})
                    .get(intent.backend, {})
                    .get("api")
                )
                if backend_api is None:
                    continue
            score = (1.0 - float(distance)) + self._lexical_bonus(intent, record)
            if intent.category == record.get("category"):
                score += 0.08
            if record.get("deprecated"):
                score -= 0.2
            if record.get("doc_quality") == "missing":
                score -= 0.03
            results.append(
                SearchResult(
                    id=item_id,
                    score=score,
                    distance=float(distance),
                    record=record,
                )
            )

        results.sort(key=lambda item: item.score, reverse=True)
        return results[: intent.top_k]

