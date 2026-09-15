"""OpenAI-compatible client for the configured Qwen service."""

from __future__ import annotations

import os
from typing import Dict, List, Optional

from openai import OpenAI


DEFAULT_BASE_URL = (
    "https://ws-s6eavmbn4d8prjq0.cn-beijing.maas.aliyuncs.com/"
    "compatible-mode/v1"
)


class QwenClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> None:
        key = api_key or os.getenv("qianwen_openai_api")
        self.model = model or os.getenv("QIANWEN_MODEL", "qwen-turbo")
        self.client = None
        if key:
            self.client = OpenAI(
                api_key=key,
                base_url=base_url or os.getenv("QIANWEN_BASE_URL", DEFAULT_BASE_URL),
                timeout=timeout or float(os.getenv("QIANWEN_TIMEOUT", "60")),
                max_retries=(
                    max_retries
                    if max_retries is not None
                    else int(os.getenv("QIANWEN_MAX_RETRIES", "2"))
                ),
            )

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
    ) -> str:
        if self.client is None:
            raise RuntimeError(
                "Environment variable 'qianwen_openai_api' is not configured"
            )
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("Qwen returned an empty response")
        return content.strip()
