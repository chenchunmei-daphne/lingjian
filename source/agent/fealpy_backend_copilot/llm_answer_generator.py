"""Grounded answer generation with template fallback."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from answer_generator import TemplateAnswerGenerator
from llm_client import QwenClient
from output_validator import GroundedAnswerValidator
from schemas import AgentAnswer, QueryIntent, SearchResult


PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "answer_prompt.txt"


def _context(result: SearchResult) -> dict:
    record = result.record
    return {
        "id": record.get("id"),
        "full_name": record.get("full_name"),
        "category": record.get("category"),
        "description": record.get("description"),
        "signature": record.get("signature"),
        "parameters": record.get("parameters"),
        "backends": record.get("backends"),
        "backend_diff_notes": record.get("backend_diff_notes"),
        "examples": record.get("examples"),
        "source": record.get("source"),
        "retrieval_score": round(result.score, 6),
    }


class LLMAnswerGenerator:
    def __init__(self, client: QwenClient) -> None:
        self.client = client
        self.fallback = TemplateAnswerGenerator()
        self.validator = GroundedAnswerValidator()
        self.prompt = PROMPT_PATH.read_text(encoding="utf-8")
        self.last_source = "template"

    def generate(
        self,
        query: str,
        intent: QueryIntent,
        results: List[SearchResult],
        history: Optional[List[dict]] = None,
    ) -> AgentAnswer:
        if not results:
            answer = self.fallback.generate(query, intent, results)
            answer.answer_source = "template_fallback"
            return answer
        try:
            prompt = (
                self.prompt
                .replace("{{QUERY}}", query)
                .replace(
                    "{{HISTORY}}",
                    json.dumps(history or [], ensure_ascii=False, indent=2),
                )
                .replace(
                    "{{INTENT}}",
                    json.dumps(asdict(intent), ensure_ascii=False, indent=2),
                )
                .replace(
                    "{{CONTEXTS}}",
                    json.dumps(
                        [_context(result) for result in results],
                        ensure_ascii=False,
                        indent=2,
                    ),
                )
            )
            text = self.client.complete([{"role": "user", "content": prompt}])
            validation = self.validator.validate(text, intent, results)
            if not validation.valid:
                answer = self.fallback.generate(query, intent, results)
                answer.answer_source = "template_validation_fallback"
                answer.validation_errors = validation.errors
                self.last_source = "template_validation_fallback"
                return answer
            self.last_source = "qwen"
            return AgentAnswer(
                matched=True,
                query=query,
                intent=intent,
                matches=results,
                text=text,
                answer_source="qwen",
                validation_errors=[],
            )
        except Exception:
            self.last_source = "template_fallback"
            answer = self.fallback.generate(query, intent, results)
            answer.answer_source = "template_fallback"
            return answer
