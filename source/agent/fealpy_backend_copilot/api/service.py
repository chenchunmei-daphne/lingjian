"""Application service that owns the heavyweight singleton objects."""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from hybrid_agent import HybridFealpyBackendAgent
from intent_parser import RuleBasedIntentParser
from schemas import QueryIntent
from vector_kb import DEFAULT_COLLECTION, DEFAULT_DB_DIR, PROJECT_DIR


LOGGER = logging.getLogger("fealpy_backend_copilot")


def _match(result) -> dict:
    record = result.record
    backends = record.get("backends") or {}
    return {
        "id": result.id,
        "score": result.score,
        "distance": result.distance,
        "full_name": record.get("full_name") or result.id,
        "category": record.get("category") or "other",
        "numpy_api": (backends.get("numpy") or {}).get("api"),
        "pytorch_api": (backends.get("pytorch") or {}).get("api"),
        "source": record.get("source"),
    }


class AgentService:
    """Load the model once and expose thread-safe application operations."""

    def __init__(self, agent=None) -> None:
        self.agent = agent
        self.ready = agent is not None
        self.error: Optional[str] = None
        self._lock = threading.RLock()
        self._rule_parser = RuleBasedIntentParser()

    def initialize(self) -> None:
        if self.ready:
            return
        with self._lock:
            if self.ready:
                return
            try:
                self.agent = HybridFealpyBackendAgent()
                self.ready = True
                self.error = None
                LOGGER.info("FEALPy assistant initialized")
            except Exception as exc:
                self.error = f"{type(exc).__name__}: {exc}"
                LOGGER.exception("Failed to initialize FEALPy assistant")
                raise

    def chat(self, query: str, session_id: str, top_k: int) -> dict:
        if not self.ready or self.agent is None:
            raise RuntimeError(self.error or "Agent service is not ready")
        request_id = uuid.uuid4().hex[:12]
        started = time.perf_counter()
        with self._lock:
            answer = self.agent.run(query, top_k=top_k, session_id=session_id)
        elapsed = time.perf_counter() - started
        LOGGER.info(
            "chat request_id=%s session_id=%s matched=%s intent=%s answer=%s elapsed=%.3f",
            request_id,
            session_id,
            answer.matched,
            answer.intent_source,
            answer.answer_source,
            elapsed,
        )
        return {
            "answer": answer.text,
            "matched": answer.matched,
            "intent": asdict(answer.intent),
            "intent_source": answer.intent_source,
            "answer_source": answer.answer_source,
            "validation_errors": answer.validation_errors,
            "matches": [_match(result) for result in answer.matches],
        }

    def search(
        self,
        query: str,
        top_k: int,
        backend: Optional[str] = None,
        category: Optional[str] = None,
    ) -> dict:
        if not self.ready or self.agent is None:
            raise RuntimeError(self.error or "Agent service is not ready")
        intent = self._rule_parser.parse(query, top_k=top_k)
        if backend:
            intent.backend = backend
        if category:
            intent.category = category
        with self._lock:
            results = self.agent.retriever.search(intent)
        return {
            "intent": asdict(intent),
            "matches": [_match(result) for result in results],
        }

    def interface(self, interface_id: str) -> Optional[dict]:
        if not self.ready or self.agent is None:
            raise RuntimeError(self.error or "Agent service is not ready")
        return self.agent.retriever.records.get(interface_id)

    def clear_session(self, session_id: str) -> None:
        if self.agent is not None:
            with self._lock:
                self.agent.clear_session(session_id)

    def health(self) -> dict:
        manifest_path = DEFAULT_DB_DIR.parent / "manifest.json"
        manifest = {}
        if manifest_path.is_file():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        database_exists = DEFAULT_DB_DIR.is_dir() and any(DEFAULT_DB_DIR.iterdir())
        return {
            "status": "ok" if self.ready else "error",
            "ready": self.ready,
            "embedding_model": bool(self.ready and self.agent),
            "vector_database": database_exists,
            "record_count": int(manifest.get("record_count", 0)),
            "qwen_configured": bool(os.getenv("qianwen_openai_api")),
            "collection": str(manifest.get("collection", DEFAULT_COLLECTION)),
            "error": self.error,
        }

