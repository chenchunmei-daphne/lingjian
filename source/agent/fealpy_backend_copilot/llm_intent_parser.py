"""Qwen-backed intent parsing with deterministic fallback."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from intent_parser import RuleBasedIntentParser
from llm_client import QwenClient
from schemas import QueryIntent


PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "intent_prompt.txt"
VALID_CATEGORIES = {
    "creation", "math", "linalg", "manipulation",
    "reduction", "comparison", "dtype", "other",
}
VALID_BACKENDS = {"numpy", "pytorch"}
VALID_PARAMETERS = {"shape", "dtype", "device", "axis", "keepdims"}


def _json_object(text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("Intent response is not a JSON object")
    return value


class LLMIntentParser:
    def __init__(self, client: QwenClient) -> None:
        self.client = client
        self.fallback = RuleBasedIntentParser()
        self.prompt = PROMPT_PATH.read_text(encoding="utf-8")
        self.last_source = "rule"

    @staticmethod
    def _safe_parameters(value: Any) -> Dict[str, Any]:
        if not isinstance(value, dict):
            return {}
        return {
            str(key): item
            for key, item in value.items()
            if key in VALID_PARAMETERS
            and isinstance(item, (str, int, float, bool, list, tuple, type(None)))
        }

    @staticmethod
    def _safe_hints(value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        return [
            str(item) for item in value[:5]
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", str(item))
        ]

    def parse(
        self,
        query: str,
        top_k: int = 5,
        history: Optional[List[dict]] = None,
        previous_intent: Optional[QueryIntent] = None,
    ) -> QueryIntent:
        rule_intent = self.fallback.parse(query, top_k=top_k)
        try:
            prompt = (
                self.prompt
                .replace("{{QUERY}}", query)
                .replace(
                    "{{HISTORY}}",
                    json.dumps(history or [], ensure_ascii=False, indent=2),
                )
            )
            raw = self.client.complete([{"role": "user", "content": prompt}])
            value = _json_object(raw)
            category = value.get("category")
            backend = value.get("backend")
            parameters = self._safe_parameters(value.get("parameters"))
            hints = self._safe_hints(value.get("interface_hints"))
            if previous_intent:
                inherited = dict(previous_intent.parameters)
                inherited.update(parameters)
                parameters = inherited
                if category not in VALID_CATEGORIES:
                    category = previous_intent.category
                if backend not in VALID_BACKENDS:
                    backend = previous_intent.backend
                if not hints:
                    hints = list(previous_intent.interface_hints)
            self.last_source = "qwen"
            return QueryIntent(
                original_query=query,
                operation=str(
                    value.get("operation")
                    or (previous_intent.operation if previous_intent else None)
                    or rule_intent.operation
                ),
                category=(
                    category if category in VALID_CATEGORIES else rule_intent.category
                ),
                backend=backend if backend in VALID_BACKENDS else rule_intent.backend,
                parameters=parameters or rule_intent.parameters,
                interface_hints=hints or rule_intent.interface_hints,
                top_k=top_k,
            )
        except Exception:
            self.last_source = "rule_fallback"
            if previous_intent:
                merged = dict(previous_intent.parameters)
                merged.update(rule_intent.parameters)
                rule_intent.parameters = merged
                rule_intent.operation = previous_intent.operation
                rule_intent.category = rule_intent.category or previous_intent.category
                rule_intent.backend = rule_intent.backend or previous_intent.backend
                rule_intent.interface_hints = (
                    rule_intent.interface_hints or previous_intent.interface_hints
                )
            return rule_intent
