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


def ask(message, history, model, session_id):
    try:
        result = service.chat(
            query=message,
            session_id=session_id,
            top_k=5,
            model=model or None,
        )
        model_used = result.get("model_used")
        suffix = f"\n\n_本次使用模型：`{model_used}`_" if model_used else ""
        return result["answer"] + suffix
    except Exception as exc:
        return f"智能体处理失败：{type(exc).__name__}: {exc}"


def clear_session(session_id):
    service.clear_session(session_id)


def load_models():
    try:
        result = service.models(refresh=False)
        choices = result.get("models") or []
        default = choices[0] if choices else result.get("default_model")
        return gr.update(choices=choices, value=default)
    except Exception:
        return gr.update(choices=[], value=None)


with gr.Blocks() as demo:
    model_selector = gr.Dropdown(
        choices=[],
        value=None,
        label="对话模型",
        info="默认优先 qwen3.7，其次 deepseek-v4；不可用时自动切换。",
        allow_custom_value=True,
    )
    session_state = gr.State(
        value=lambda: uuid.uuid4().hex,
        time_to_live=3600,
        delete_callback=clear_session,
    )
    gr.ChatInterface(
        fn=ask,
        additional_inputs=[model_selector, session_state],
        title="FEALPy 多后端接口助手",
        description="描述计算功能，检索匹配的 FEALPy bm 接口；可选择对话模型。",
    )
    demo.load(load_models, inputs=None, outputs=model_selector)

fastapi_app = create_app(service)


@fastapi_app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/chat/")


app = gr.mount_gradio_app(fastapi_app, demo, path="/chat")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("FEALPY_HOST", "0.0.0.0"),
        port=int(os.getenv("FEALPY_PORT", "8000")),
    )
