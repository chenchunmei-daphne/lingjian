"""Request and response models for the HTTP API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(default="default", min_length=1, max_length=128)
    top_k: int = Field(default=5, ge=1, le=20)


class MatchResponse(BaseModel):
    id: str
    score: float
    distance: float
    full_name: str
    category: str
    numpy_api: Optional[str] = None
    pytorch_api: Optional[str] = None
    source: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    matched: bool
    intent: Dict[str, Any]
    intent_source: str
    answer_source: str
    validation_errors: List[str]
    matches: List[MatchResponse]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    backend: Optional[str] = Field(default=None, pattern="^(numpy|pytorch)$")
    category: Optional[str] = Field(
        default=None,
        pattern="^(creation|math|linalg|manipulation|reduction|comparison|dtype|other)$",
    )


class SearchResponse(BaseModel):
    intent: Dict[str, Any]
    matches: List[MatchResponse]


class HealthResponse(BaseModel):
    status: str
    ready: bool
    embedding_model: bool
    vector_database: bool
    record_count: int
    qwen_configured: bool
    collection: str
    error: Optional[str] = None

