"""Grounded, template-based answers without a generative language model."""

from __future__ import annotations

import json
from typing import Dict, List

from schemas import AgentAnswer, QueryIntent, SearchResult


def _format_value(value) -> str:
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, list):
        return repr(tuple(value))
    return repr(value)


def _example(record: Dict, intent: QueryIntent) -> str:
    configured = record.get("examples") or []
    if configured and not intent.parameters:
        return configured[0].get("code") or ""

    backend = intent.backend or "numpy"
    name = record["full_name"]
    arguments: List[str] = []
    parameter_names = {item.get("name") for item in record.get("parameters") or []}

    if "shape" in intent.parameters and "shape" in parameter_names:
        arguments.append(_format_value(intent.parameters["shape"]))
    elif name in {"bm.zeros", "bm.ones", "bm.empty"}:
        arguments.append("(2, 3)")
    elif name in {"bm.tensor", "bm.array", "bm.asarray"}:
        arguments.append("[1, 2, 3]")
    else:
        required = [
            item["name"] for item in record.get("parameters") or []
            if item.get("required") and item.get("name") != "shape"
        ]
        arguments.extend(required)

    for key in ("dtype", "axis", "device"):
        if key in intent.parameters and key in parameter_names:
            arguments.append(f"{key}={_format_value(intent.parameters[key])}")

    return (
        "from fealpy.backend import bm\n"
        f"bm.set_backend(\"{backend}\")\n"
        f"result = {name}({', '.join(arguments)})"
    )


class TemplateAnswerGenerator:
    def generate(
        self,
        query: str,
        intent: QueryIntent,
        results: List[SearchResult],
    ) -> AgentAnswer:
        if not results:
            text = "没有找到满足当前分类和后端条件的 FEALPy 接口。"
            return AgentAnswer(False, query, intent, [], text)

        best = results[0]
        record = best.record
        backends = record.get("backends") or {}
        numpy_api = (backends.get("numpy") or {}).get("api") or "无单一对应 API"
        pytorch_api = (backends.get("pytorch") or {}).get("api") or "无单一对应 API"
        parameters = record.get("parameters") or []
        parameter_lines = [
            f"- `{item.get('name')}` ({item.get('type') or '未标注类型'})："
            f"{item.get('description') or '无说明'}"
            for item in parameters
        ] or ["- 无参数"]
        alternatives = "、".join(f"`{item.id}`" for item in results[1:3]) or "无"

        text = "\n".join([
            f"推荐接口：`{record['full_name']}`",
            "",
            f"功能：{record.get('description') or '无说明'}",
            f"签名：`{record.get('signature') or '未提供'}`",
            "",
            "主要参数：",
            *parameter_lines,
            "",
            "对应后端：",
            f"- NumPy：`{numpy_api}`",
            f"- PyTorch：`{pytorch_api}`",
            "",
            f"后端差异：{record.get('backend_diff_notes') or '无'}",
            "",
            "使用示例：",
            "```python",
            _example(record, intent),
            "```",
            "",
            f"其他候选：{alternatives}",
            f"源码：`{record.get('source') or '未知'}`",
            f"匹配分数：{best.score:.4f}",
        ])
        return AgentAnswer(True, query, intent, results, text)

