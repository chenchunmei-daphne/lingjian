"""Deterministic intent extraction for common FEALPy questions."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional

from schemas import QueryIntent


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "creation": ["创建", "生成", "初始化", "随机", "全零", "全一", "张量"],
    "linalg": ["范数", "矩阵乘", "线性方程", "方程组", "求逆", "特征值", "分解"],
    "reduction": ["求和", "平均", "均值", "最大值", "最小值", "归约", "方差"],
    "math": ["正弦", "余弦", "指数", "对数", "平方根", "绝对值"],
    "manipulation": ["变形", "形状", "转置", "拼接", "堆叠", "维度", "切分"],
    "comparison": ["比较", "相等", "大于", "小于", "逻辑"],
    "dtype": ["数据类型", "dtype", "设备", "device", "转换类型"],
}

INTERFACE_HINTS: Dict[str, List[str]] = {
    "random.randn": ["正态", "高斯", "标准正态", "randn"],
    "random.rand": ["均匀随机", "均匀分布", "rand"],
    "random.randint": ["随机整数", "randint"],
    "zeros": ["全零", "零张量", "zeros"],
    "ones": ["全一", "一张量", "ones"],
    "tensor": ["创建张量", "tensor"],
    "arange": ["等差", "序列", "arange"],
    "linspace": ["等间隔", "等分", "linspace"],
    "linalg.solve": ["线性方程", "方程组", "ax=b", "solve"],
    "linalg.vector_norm": ["向量范数", "vector norm"],
    "linalg.matrix_norm": ["矩阵范数", "frobenius", "frobenius范数"],
    "matmul": ["矩阵乘法", "矩阵相乘", "matmul"],
    "einsum": ["爱因斯坦", "einsum"],
    "sum": ["求和", "sum"],
    "mean": ["平均", "均值", "mean"],
    "reshape": ["变形", "重塑", "reshape"],
    "transpose": ["转置", "transpose"],
    "concat": ["拼接", "连接张量", "concat"],
    "stack": ["堆叠", "stack"],
}


def _first_category(query: str) -> Optional[str]:
    scores = {
        category: sum(keyword.lower() in query for keyword in keywords)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] else None


def _interface_hints(query: str) -> List[str]:
    matches = []
    for interface, keywords in INTERFACE_HINTS.items():
        if any(keyword.lower() in query for keyword in keywords):
            matches.append(interface)
    return matches


def _extract_shape(query: str) -> Optional[List[int]]:
    match = re.search(r"(?<!\d)(\d+)\s*[x×X*]\s*(\d+)(?!\d)", query)
    if match:
        return [int(match.group(1)), int(match.group(2))]
    match = re.search(r"(?:shape|形状)\s*[=:：]?\s*[\[(]([\d,，\s]+)[\])]", query)
    if match:
        values = [int(value) for value in re.findall(r"\d+", match.group(1))]
        return values or None
    return None


def _extract_parameters(query: str, backend: Optional[str]) -> Dict[str, object]:
    parameters: Dict[str, object] = {}
    shape = _extract_shape(query)
    if shape:
        parameters["shape"] = shape

    dtype_match = re.search(
        r"\b(float16|float32|float64|int8|int16|int32|int64|bool)\b",
        query,
        flags=re.IGNORECASE,
    )
    if dtype_match:
        parameters["dtype"] = dtype_match.group(1).lower()

    axis_match = re.search(r"(?:axis|轴)\s*[=:：]?\s*(-?\d+)", query, flags=re.IGNORECASE)
    if axis_match:
        parameters["axis"] = int(axis_match.group(1))

    if "cuda" in query or "gpu" in query:
        parameters["device"] = "cuda"
    elif backend == "pytorch" and "cpu" in query:
        parameters["device"] = "cpu"
    return parameters


class RuleBasedIntentParser:
    def parse(self, query: str, top_k: int = 5) -> QueryIntent:
        normalized = " ".join(query.strip().lower().split())
        backend = None
        if any(token in normalized for token in ("pytorch", "torch", "cuda", "gpu")):
            backend = "pytorch"
        elif any(token in normalized for token in ("numpy", "np.")):
            backend = "numpy"

        hints = _interface_hints(normalized)
        category = _first_category(normalized)
        if hints and hints[0].startswith(("linalg.",)):
            category = "linalg"
        operation = hints[0] if hints else normalized
        return QueryIntent(
            original_query=query,
            operation=operation,
            category=category,
            backend=backend,
            parameters=_extract_parameters(normalized, backend),
            interface_hints=hints,
            top_k=top_k,
        )

