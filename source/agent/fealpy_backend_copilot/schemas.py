"""Data structures used by the rule-based FEALPy assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class QueryIntent:
    original_query: str
    operation: str
    category: Optional[str] = None
    backend: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    interface_hints: List[str] = field(default_factory=list)
    top_k: int = 5


@dataclass
class SearchResult:
    id: str
    score: float
    distance: float
    record: Dict[str, Any]


@dataclass
class AgentAnswer:
    matched: bool
    query: str
    intent: QueryIntent
    matches: List[SearchResult]
    text: str
    intent_source: str = "rule"
    answer_source: str = "template"
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class ConversationTurn:
    query: str
    answer: str
    intent: QueryIntent
    interface_ids: List[str] = field(default_factory=list)
