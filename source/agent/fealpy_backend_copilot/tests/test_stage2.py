"""Automated tests for conversation, validation, and fallback behavior."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from conversation import ConversationMemory
from llm_answer_generator import LLMAnswerGenerator
from llm_client import QwenClient
from llm_intent_parser import LLMIntentParser
from output_validator import GroundedAnswerValidator
from schemas import AgentAnswer, QueryIntent, SearchResult


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)

    def complete(self, messages, temperature=0.0):
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def zeros_result() -> SearchResult:
    return SearchResult(
        id="bm.zeros",
        score=0.9,
        distance=0.1,
        record={
            "id": "bm.zeros",
            "full_name": "bm.zeros",
            "category": "creation",
            "description": "创建全零张量",
            "signature": "zeros(shape, *, dtype=None, device=None)",
            "parameters": [
                {"name": "shape", "type": "Size", "required": True, "description": "张量形状"},
                {"name": "device", "type": None, "required": False, "description": "计算设备"},
            ],
            "backends": {
                "numpy": {"api": "numpy.zeros"},
                "pytorch": {"api": "torch.zeros"},
            },
            "backend_diff_notes": "PyTorch 支持设备参数",
            "examples": [],
            "source": "fealpy/backend/numpy_backend.py:L646",
        },
    )


class IntentTests(unittest.TestCase):
    def test_missing_api_key_is_deferred_to_fallback(self):
        client = QwenClient(api_key="")
        client.client = None
        with self.assertRaises(RuntimeError):
            client.complete([{"role": "user", "content": "test"}])

    def test_follow_up_inherits_previous_intent(self):
        client = FakeClient([
            json.dumps({
                "operation": "转到 GPU",
                "category": None,
                "backend": "pytorch",
                "parameters": {"device": "cuda"},
                "interface_hints": [],
            }, ensure_ascii=False)
        ])
        parser = LLMIntentParser(client)
        previous = QueryIntent(
            original_query="创建 3×4 全零张量",
            operation="创建全零张量",
            category="creation",
            parameters={"shape": [3, 4]},
            interface_hints=["zeros"],
        )
        intent = parser.parse("那放到 GPU 上呢？", previous_intent=previous)
        self.assertEqual(intent.category, "creation")
        self.assertEqual(intent.backend, "pytorch")
        self.assertEqual(intent.parameters, {"shape": [3, 4], "device": "cuda"})
        self.assertEqual(intent.interface_hints, ["zeros"])

    def test_invalid_intent_fields_are_sanitized(self):
        client = FakeClient([json.dumps({
            "operation": "测试",
            "category": "invented",
            "backend": "cuda-backend",
            "parameters": {"unsafe": "value", "axis": 1},
            "interface_hints": ["zeros", "bad hint!"],
        })])
        intent = LLMIntentParser(client).parse("axis=1 求和")
        self.assertNotEqual(intent.category, "invented")
        self.assertNotEqual(intent.backend, "cuda-backend")
        self.assertEqual(intent.parameters, {"axis": 1})
        self.assertEqual(intent.interface_hints, ["zeros"])


class ConversationTests(unittest.TestCase):
    def test_memory_is_bounded_and_clearable(self):
        memory = ConversationMemory(max_turns=2)
        intent = QueryIntent("q", "op")
        for index in range(3):
            memory.add("s1", AgentAnswer(True, f"q{index}", intent, [], f"a{index}"))
        self.assertEqual([turn.query for turn in memory.turns("s1")], ["q1", "q2"])
        memory.clear("s1")
        self.assertEqual(memory.turns("s1"), [])


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.intent = QueryIntent("创建全零张量", "zeros", "creation")
        self.results = [zeros_result()]

    def test_grounded_answer_passes(self):
        result = GroundedAnswerValidator().validate(
            "使用 bm.zeros，对应 numpy.zeros 和 torch.zeros。",
            self.intent,
            self.results,
        )
        self.assertTrue(result.valid)

    def test_hallucinated_interface_and_api_fail(self):
        result = GroundedAnswerValidator().validate(
            "使用 bm.magic，对应 torch.magic。",
            self.intent,
            self.results,
        )
        self.assertFalse(result.valid)
        self.assertGreaterEqual(len(result.errors), 2)

    def test_generator_falls_back_after_validation_failure(self):
        generator = LLMAnswerGenerator(
            FakeClient(["建议使用 bm.magic，对应 torch.magic。"])
        )
        answer = generator.generate("创建全零张量", self.intent, self.results)
        self.assertEqual(answer.answer_source, "template_validation_fallback")
        self.assertTrue(answer.validation_errors)
        self.assertIn("bm.zeros", answer.text)

    def test_generator_falls_back_on_api_error(self):
        generator = LLMAnswerGenerator(FakeClient([RuntimeError("offline")]))
        answer = generator.generate("创建全零张量", self.intent, self.results)
        self.assertEqual(answer.answer_source, "template_fallback")
        self.assertIn("bm.zeros", answer.text)


if __name__ == "__main__":
    unittest.main()
