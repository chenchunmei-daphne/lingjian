"""Single-process FastAPI + Gradio application."""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

# These variables must be set before importing Gradio/Hugging Face packages.
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

import gradio as gr
import uvicorn
from fastapi.responses import RedirectResponse


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from api.app import create_app
from api.service import AgentService


service = AgentService()


def ask(message, history, session_id):
    try:
        return service.chat(
            query=message,
            session_id=session_id,
            top_k=5,
        )["answer"]
    except Exception as exc:
        return f"智能体处理失败：{type(exc).__name__}: {exc}"


def clear_session(session_id):
    service.clear_session(session_id)


demo = gr.ChatInterface(
    fn=ask,
    additional_inputs=[
        gr.State(
            value=lambda: uuid.uuid4().hex,
            time_to_live=3600,
            delete_callback=clear_session,
        )
    ],
    title="FEALPy 多后端接口助手",
    description="询问 FEALPy bm 接口、参数和 NumPy/PyTorch 后端映射。",
)

fastapi_app = create_app(service)


@fastapi_app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/chat/")


app = gr.mount_gradio_app(fastapi_app, demo, path="/chat")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("FEALPY_HOST", "127.0.0.1"),
        port=int(os.getenv("FEALPY_PORT", "8000")),
    )
