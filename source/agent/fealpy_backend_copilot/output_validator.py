"""Validate that generated answers stay grounded in retrieved records."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Set

from schemas import QueryIntent, SearchResult


BM_PATTERN = re.compile(r"\bbm\.[A-Za-z_][A-Za-z0-9_.]*")
API_PATTERN = re.compile(
    r"\b(?:numpy|torch)(?:\.[A-Za-z_][A-Za-z0-9_]*)+"
)
ALLOWED_BM_UTILITIES = {
    "bm.set_backend",
    "bm.bool",
    "bm.int8", "bm.int16", "bm.int32", "bm.int64",
    "bm.uint8", "bm.uint16", "bm.uint32", "bm.uint64",
    "bm.float16", "bm.float32", "bm.float64",
    "bm.complex64", "bm.complex128",
}


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)


class GroundedAnswerValidator:
    def validate(
        self,
        text: str,
        intent: QueryIntent,
        results: List[SearchResult],
    ) -> ValidationResult:
        errors: List[str] = []
        allowed_ids: Set[str] = {item.id for item in results}
        mentioned_ids = set(BM_PATTERN.findall(text))
        unknown_ids = mentioned_ids.difference(allowed_ids, ALLOWED_BM_UTILITIES)
        if unknown_ids:
            errors.append(f"Unretrieved FEALPy interfaces: {sorted(unknown_ids)}")
        if allowed_ids and not mentioned_ids.intersection(allowed_ids):
            errors.append("No retrieved FEALPy interface was cited")

        allowed_apis: Set[str] = set()
        for result in results:
            for backend in (result.record.get("backends") or {}).values():
                api = backend.get("api")
                if api:
                    allowed_apis.add(api)
        mentioned_apis = set(API_PATTERN.findall(text))
        unknown_apis = mentioned_apis.difference(allowed_apis)
        if unknown_apis:
            errors.append(f"Unsupported backend APIs: {sorted(unknown_apis)}")

        if intent.backend and results:
            best_backend = (
                results[0].record.get("backends", {})
                .get(intent.backend, {})
                .get("api")
            )
            if best_backend is None:
                errors.append(f"Top result does not support backend: {intent.backend}")
        return ValidationResult(valid=not errors, errors=errors)
