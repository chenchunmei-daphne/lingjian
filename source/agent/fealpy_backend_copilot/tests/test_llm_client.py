from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from llm_client import QwenClient


class FakeStatusError(Exception):
    def __init__(self, message, status_code, body=None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body
        self.response = None


class FakeModels:
    def __init__(self, ids):
        self.ids = ids
        self.calls = 0

    def list(self):
        self.calls += 1
        return SimpleNamespace(
            data=[SimpleNamespace(id=item) for item in self.ids]
        )


class FakeCompletions:
    def __init__(self, outcomes):
        self.outcomes = outcomes
        self.calls = []

    def create(self, model, messages, temperature):
        del messages, temperature
        self.calls.append(model)
        outcome = self.outcomes.get(model, f"response from {model}")
        if isinstance(outcome, Exception):
            raise outcome
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=outcome))]
        )


def make_client(model_ids, outcomes=None):
    client = QwenClient(
        api_key="",
        model="fallback-model",
        model_cache_seconds=300,
        unavailable_cache_seconds=300,
    )
    completions = FakeCompletions(outcomes or {})
    client.client = SimpleNamespace(
        models=FakeModels(model_ids),
        chat=SimpleNamespace(completions=completions),
    )
    return client, completions


class ModelSelectionTests(unittest.TestCase):
    def test_preferred_families_are_ranked_first(self):
        client, _ = make_client([
            "other-chat", "deepseek-v4-large", "qwen3.7-plus",
            "text-embedding-model",
        ])

        models = client.list_models()

        self.assertEqual(models[:2], ["qwen3.7-plus", "deepseek-v4-large"])
        self.assertNotIn("text-embedding-model", models)

    def test_quota_failure_falls_through_to_deepseek(self):
        client, completions = make_client(
            ["qwen3.7-plus", "deepseek-v4-large", "other-chat"],
            {
                "qwen3.7-plus": FakeStatusError(
                    "insufficient quota", 429, {"code": "insufficient_quota"}
                ),
                "deepseek-v4-large": "ok",
            },
        )

        result = client.complete([{"role": "user", "content": "hello"}])

        self.assertEqual(result, "ok")
        self.assertEqual(
            completions.calls[:2], ["qwen3.7-plus", "deepseek-v4-large"]
        )
        self.assertEqual(client.last_model, "deepseek-v4-large")

        completions.calls.clear()
        client.complete(
            [{"role": "user", "content": "second stage"}],
            model="qwen3.7-plus",
        )
        self.assertEqual(completions.calls[0], "deepseek-v4-large")

    def test_user_selected_model_is_attempted_first(self):
        client, completions = make_client(
            ["qwen3.7-plus", "deepseek-v4-large", "other-chat"]
        )

        client.complete(
            [{"role": "user", "content": "hello"}], model="other-chat"
        )

        self.assertEqual(completions.calls[0], "other-chat")
        self.assertEqual(client.last_model, "other-chat")

    def test_authentication_failure_does_not_switch_models(self):
        client, completions = make_client(
            ["qwen3.7-plus", "deepseek-v4-large"],
            {"qwen3.7-plus": FakeStatusError("invalid key", 401)},
        )

        with self.assertRaises(FakeStatusError):
            client.complete([{"role": "user", "content": "hello"}])

        self.assertEqual(completions.calls, ["qwen3.7-plus"])


if __name__ == "__main__":
    unittest.main()
