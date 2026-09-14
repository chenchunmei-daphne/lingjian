"""FastAPI application factory."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from api.service import AgentService


def create_app(service=None) -> FastAPI:
    agent_service = service or AgentService()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        agent_service.initialize()
        yield

    app = FastAPI(
        title="FEALPy Backend Copilot",
        version="0.1.0",
        description="RAG assistant for FEALPy NumPy/PyTorch backend interfaces.",
        lifespan=lifespan,
    )
    app.state.agent_service = agent_service
    app.include_router(router)
    return app


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
app = create_app()

