"""FastAPI routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool

from api.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SearchRequest,
    SearchResponse,
)


router = APIRouter()


def _service(request: Request):
    return request.app.state.agent_service


@router.get("/health", response_model=HealthResponse)
async def health(request: Request):
    return _service(request).health()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request):
    try:
        return await run_in_threadpool(
            _service(request).chat,
            payload.query,
            payload.session_id,
            payload.top_k,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/api/search", response_model=SearchResponse)
async def search(payload: SearchRequest, request: Request):
    try:
        return await run_in_threadpool(
            _service(request).search,
            payload.query,
            payload.top_k,
            payload.backend,
            payload.category,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/api/interfaces/{interface_id:path}")
async def interface(interface_id: str, request: Request):
    try:
        record = _service(request).interface(interface_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if record is None:
        raise HTTPException(status_code=404, detail="Interface not found")
    return record


@router.delete("/api/sessions/{session_id}", status_code=204)
async def clear_session(session_id: str, request: Request):
    _service(request).clear_session(session_id)

