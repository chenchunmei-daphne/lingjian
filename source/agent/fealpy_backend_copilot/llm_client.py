"""OpenAI-compatible client with model discovery and quota failover."""

from __future__ import annotations

import os
import re
import threading
import time
from typing import Dict, Iterable, List, Optional

from openai import OpenAI


DEFAULT_BASE_URL = (
    "https://ws-s6eavmbn4d8prjq0.cn-beijing.maas.aliyuncs.com/"
    "compatible-mode/v1"
)
DEFAULT_MODEL = "qwen-turbo"
DEFAULT_PRIORITY_FAMILIES = ("qwen3.7", "deepseek-v4")
NON_CHAT_MARKERS = (
    "embedding", "rerank", "tts", "whisper", "transcrib", "image",
    "video", "audio", "moderation", "speech",
)
FAILOVER_MARKERS = (
    "quota", "insufficient_quota", "balance", "credit", "exhausted",
    "allocation", "capacity", "rate limit", "rate_limit", "too many requests",
    "model not found", "model_not_found", "does not exist", "not available",
    "no permission", "permission", "额度", "余额", "限流", "无权", "不可用",
)


def _deduplicate(values: Iterable[str]) -> List[str]:
    return list(dict.fromkeys(value.strip() for value in values if value.strip()))


class QwenClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        model_cache_seconds: Optional[float] = None,
        unavailable_cache_seconds: Optional[float] = None,
    ) -> None:
        key = api_key or os.getenv("qianwen_openai_api")
        self.model = model or os.getenv("QIANWEN_MODEL", DEFAULT_MODEL)
        configured_fallbacks = os.getenv("QIANWEN_FALLBACK_MODELS", "")
        self.configured_fallbacks = _deduplicate(configured_fallbacks.split(","))
        configured_families = os.getenv(
            "QIANWEN_MODEL_PRIORITY", ",".join(DEFAULT_PRIORITY_FAMILIES)
        )
        self.priority_families = tuple(
            item.lower() for item in _deduplicate(configured_families.split(","))
        )
        self.model_cache_seconds = (
            model_cache_seconds
            if model_cache_seconds is not None
            else float(os.getenv("QIANWEN_MODEL_CACHE_SECONDS", "300"))
        )
        self.unavailable_cache_seconds = (
            unavailable_cache_seconds
            if unavailable_cache_seconds is not None
            else float(os.getenv("QIANWEN_UNAVAILABLE_CACHE_SECONDS", "300"))
        )
        self.client = None
        self.last_model: Optional[str] = None
        self.last_attempted_models: List[str] = []
        self._models_cache: List[str] = []
        self._models_cached_at = 0.0
        self._unavailable_until: Dict[str, float] = {}
        self._lock = threading.RLock()
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

    @staticmethod
    def _is_chat_candidate(model_id: str) -> bool:
        lowered = model_id.lower()
        return not any(marker in lowered for marker in NON_CHAT_MARKERS)

    def _family_rank(self, model_id: str) -> int:
        normalized = re.sub(r"[-_.]", "", model_id.lower())
        for index, family in enumerate(self.priority_families):
            family_normalized = re.sub(r"[-_.]", "", family)
            if family_normalized in normalized:
                return index
        return len(self.priority_families)

    def rank_models(
        self,
        model_ids: Iterable[str],
        selected_model: Optional[str] = None,
    ) -> List[str]:
        """Order models by explicit selection, preferred family, then name."""
        ids = _deduplicate(model_ids)
        selected = selected_model.strip() if selected_model else None
        ordered = sorted(ids, key=lambda item: (self._family_rank(item), item.lower()))
        if self.model in ordered:
            ordered.remove(self.model)
            default_position = next(
                (
                    index for index, item in enumerate(ordered)
                    if self._family_rank(item) >= len(self.priority_families)
                ),
                len(ordered),
            )
            ordered.insert(default_position, self.model)
        if selected:
            if selected in ordered:
                ordered.remove(selected)
            ordered.insert(0, selected)
        return ordered

    def list_models(self, refresh: bool = False) -> List[str]:
        """Return visible chat-like model IDs, ordered by configured priority."""
        if self.client is None:
            return self.rank_models([self.model, *self.configured_fallbacks])
        now = time.monotonic()
        with self._lock:
            if (
                not refresh
                and self._models_cache
                and now - self._models_cached_at < self.model_cache_seconds
            ):
                return list(self._models_cache)
            response = self.client.models.list()
            model_ids = [
                str(item.id) for item in response.data
                if getattr(item, "id", None)
                and self._is_chat_candidate(str(item.id))
            ]
            model_ids.extend([self.model, *self.configured_fallbacks])
            self._models_cache = self.rank_models(model_ids)
            self._models_cached_at = now
            return list(self._models_cache)

    @staticmethod
    def _error_text(exc: Exception) -> str:
        parts = [str(exc)]
        body = getattr(exc, "body", None)
        if body is not None:
            parts.append(str(body))
        response = getattr(exc, "response", None)
        if response is not None:
            try:
                parts.append(response.text)
            except Exception:
                pass
        return " ".join(parts).lower()

    @classmethod
    def _is_failover_error(cls, exc: Exception) -> bool:
        status = getattr(exc, "status_code", None)
        text = cls._error_text(exc)
        if status == 401:
            return False
        if status in {404, 429} or (isinstance(status, int) and status >= 500):
            return True
        if status in {400, 403, 422}:
            return any(marker in text for marker in FAILOVER_MARKERS)
        return any(marker in text for marker in FAILOVER_MARKERS)

    def _candidate_models(self, selected_model: Optional[str]) -> List[str]:
        try:
            visible = self.list_models()
        except Exception:
            visible = self.rank_models([self.model, *self.configured_fallbacks])
        candidates = self.rank_models(visible, selected_model=selected_model)
        now = time.monotonic()
        return [
            item for item in candidates
            if self._unavailable_until.get(item, 0.0) <= now
        ]

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        model: Optional[str] = None,
    ) -> str:
        if self.client is None:
            raise RuntimeError(
                "Environment variable 'qianwen_openai_api' is not configured"
            )

        candidates = self._candidate_models(model)
        if not candidates:
            raise RuntimeError("No available chat model candidates")
        self.last_model = None
        self.last_attempted_models = []
        last_error: Optional[Exception] = None
        for candidate in candidates:
            self.last_attempted_models.append(candidate)
            try:
                completion = self.client.chat.completions.create(
                    model=candidate,
                    messages=messages,
                    temperature=temperature,
                )
                content = completion.choices[0].message.content
                if not content:
                    raise RuntimeError(f"Model {candidate} returned an empty response")
                self.last_model = candidate
                self._unavailable_until.pop(candidate, None)
                return content.strip()
            except Exception as exc:
                last_error = exc
                if not self._is_failover_error(exc):
                    raise
                self._unavailable_until[candidate] = (
                    time.monotonic() + self.unavailable_cache_seconds
                )
        attempted = ", ".join(self.last_attempted_models)
        raise RuntimeError(
            f"All model candidates failed ({attempted}): {last_error}"
        ) from last_error
