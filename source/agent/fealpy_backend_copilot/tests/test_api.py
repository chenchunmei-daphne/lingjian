"""API contract tests using a lightweight fake service."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from fastapi.testclient import TestClient

from api.app import create_app


class FakeService:
    def __init__(self):
        self.ready = True
        self.cleared = []

    def initialize(self):
        self.ready = True

    def health(self):
        return {
            "status": "ok", "ready": True, "embedding_model": True,
            "vector_database": True, "record_count": 220,
            "qwen_configured": True, "collection": "fealpy_interfaces",
            "error": None,
        }

    def chat(self, query, session_id, top_k):
        return {
            "answer": "使用 bm.zeros。", "matched": True,
            "intent": {"original_query": query, "operation": "zeros"},
            "intent_source": "qwen", "answer_source": "qwen",
            "validation_errors": [], "matches": [],
        }

    def search(self, query, top_k, backend, category):
        return {"intent": {"original_query": query}, "matches": []}

    def interface(self, interface_id):
        return {"id": "bm.zeros"} if interface_id == "bm.zeros" else None

    def clear_session(self, session_id):
        self.cleared.append(session_id)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()
        self.client_context = TestClient(create_app(self.service))
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["record_count"], 220)

    def test_chat(self):
        response = self.client.post(
            "/api/chat",
            json={"query": "创建全零张量", "session_id": "u1", "top_k": 3},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer_source"], "qwen")

    def test_chat_validation(self):
        response = self.client.post("/api/chat", json={"query": ""})
        self.assertEqual(response.status_code, 422)

    def test_interface(self):
        self.assertEqual(
            self.client.get("/api/interfaces/bm.zeros").json()["id"],
            "bm.zeros",
        )
        self.assertEqual(
            self.client.get("/api/interfaces/bm.unknown").status_code,
            404,
        )

    def test_clear_session(self):
        response = self.client.delete("/api/sessions/u1")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.service.cleared, ["u1"])


if __name__ == "__main__":
    unittest.main()
