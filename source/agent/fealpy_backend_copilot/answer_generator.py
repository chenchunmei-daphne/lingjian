"""Grounded interface-routing answers for the v02 retrieval MVP."""

from __future__ import annotations

from typing import List

from schemas import AgentAnswer, QueryIntent, SearchResult


class TemplateAnswerGenerator:
    def generate(
        self,
        query: str,
        intent: QueryIntent,
        results: List[SearchResult],
    ) -> AgentAnswer:
        if not results:
            text = "没有找到与该计算功能匹配的 FEALPy 接口。"
            return AgentAnswer(False, query, intent, [], text)

        best = results[0]
        record = best.record
        name = record.get("full_name") or record.get("id") or best.id
        summary = (
            record.get("match_reason")
            or record.get("summary")
            or record.get("description")
            or "该接口与描述的计算功能最匹配"
        )
        alternatives = "、".join(
            f"`{item.record.get('full_name') or item.id}`"
            for item in results[1:3]
        ) or "无"

        text = "\n".join([
            f"推荐接口：`{name}`",
            "",
            f"理由：{summary}",
            "",
            "当前知识库用于定位正确接口，具体参数和调用方式请查看该接口的代码补全或源码注释。",
            "",
            f"其他候选：{alternatives}",
        ])
        return AgentAnswer(True, query, intent, results, text)
