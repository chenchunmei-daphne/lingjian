"""Shared utilities for the FEALPy interface vector knowledge base."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


PROJECT_DIR = Path(__file__).resolve().parent
REPO_DIR = PROJECT_DIR.parents[3]
DEFAULT_DATA_FILE = PROJECT_DIR / "data" / "all_interfaces.json"
DEFAULT_MODEL_DIR = REPO_DIR / "download_model" / "bge-m3"
DEFAULT_DB_DIR = PROJECT_DIR / "vector_store" / "chroma"
DEFAULT_COLLECTION = "fealpy_interfaces"


def load_interfaces(path: Path) -> List[Dict[str, Any]]:
    """Load and minimally validate interface records."""
    with path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(f"Expected a JSON array in {path}")

    seen = set()
    required = {"id", "full_name", "category", "signature", "backends"}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"Record {index} is not an object")
        missing = required.difference(record)
        if missing:
            raise ValueError(f"Record {index} is missing fields: {sorted(missing)}")
        if record["id"] in seen:
            raise ValueError(f"Duplicate interface id: {record['id']}")
        seen.add(record["id"])
    return records


def _backend_line(name: str, backend: Dict[str, Any]) -> str:
    api = backend.get("api") or "无单一对应 API"
    signature = backend.get("signature") or "未提供"
    notes = backend.get("notes") or ""
    return f"{name}: API={api}; 签名={signature}; 说明={notes}"


def record_to_document(record: Dict[str, Any]) -> str:
    """Render one complete, self-contained text chunk for embedding."""
    parameters = record.get("parameters") or []
    parameter_text = "; ".join(
        f"{item.get('name')} ({item.get('type') or '未标注类型'}, "
        f"默认值={item.get('default') if item.get('default') is not None else '无'}): "
        f"{item.get('description') or ''}"
        for item in parameters
    ) or "无参数"

    aliases = "、".join(record.get("aliases") or []) or "无"
    keywords = "、".join(record.get("keywords") or []) or "无"
    backends = record.get("backends") or {}

    lines = [
        f"FEALPy 接口：{record['full_name']}",
        f"功能分类：{record.get('category') or 'other'}",
        f"中文别名：{aliases}",
        f"功能描述：{record.get('description') or ''}",
        f"FEALPy 签名：{record.get('signature') or '未提供'}",
        f"参数：{parameter_text}",
        _backend_line("NumPy", backends.get("numpy") or {}),
        _backend_line("PyTorch", backends.get("pytorch") or {}),
        f"后端差异：{record.get('backend_diff_notes') or '无'}",
        f"检索关键词：{keywords}",
        f"源码：{record.get('source') or '未知'}",
    ]
    return "\n".join(lines)


def record_to_metadata(record: Dict[str, Any]) -> Dict[str, Any]:
    """Create scalar-only Chroma metadata for filtering and display."""
    backends = record.get("backends") or {}
    numpy_api = (backends.get("numpy") or {}).get("api")
    pytorch_api = (backends.get("pytorch") or {}).get("api")
    return {
        "full_name": record["full_name"],
        "category": record.get("category") or "other",
        "numpy_api": numpy_api or "",
        "pytorch_api": pytorch_api or "",
        "source": record.get("source") or "",
        "doc_quality": record.get("doc_quality") or "missing",
        "deprecated": bool(record.get("deprecated", False)),
    }


def batched(items: List[Any], size: int) -> Iterable[List[Any]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]
