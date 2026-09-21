"""Utilities for the capability-centred v02 vector knowledge base."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


PROJECT_DIR = Path(__file__).resolve().parent
REPO_DIR = PROJECT_DIR.parents[3]
DEFAULT_DATA_FILE = PROJECT_DIR / "data" / "data_v02" / "all_interfaces.json"
DEFAULT_MODEL_DIR = REPO_DIR / "download_model" / "bge-m3"
DEFAULT_STORE_DIR = PROJECT_DIR / "vector_store" / "vector_store_v02"
DEFAULT_DB_DIR = DEFAULT_STORE_DIR / "chroma"
DEFAULT_COLLECTION = "fealpy_capabilities_v02"


def load_dataset(path: Path) -> Dict[str, Any]:
    """Load and validate the references needed to build the v02 index."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    required_top_level = {
        "schema_version", "dataset_version", "scope", "interfaces", "capabilities"
    }
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    missing = required_top_level.difference(data)
    if missing:
        raise ValueError(f"Dataset is missing fields: {sorted(missing)}")

    interfaces = data["interfaces"]
    capabilities = data["capabilities"]
    if not isinstance(interfaces, list) or not isinstance(capabilities, list):
        raise ValueError("interfaces and capabilities must be arrays")

    interface_ids = [item.get("id") for item in interfaces]
    capability_ids = [item.get("id") for item in capabilities]
    if None in interface_ids or len(interface_ids) != len(set(interface_ids)):
        raise ValueError("Interface IDs must be present and unique")
    if None in capability_ids or len(capability_ids) != len(set(capability_ids)):
        raise ValueError("Capability IDs must be present and unique")

    known_interfaces = set(interface_ids)
    for capability in capabilities:
        required = {"id", "intent", "expressions", "target_interfaces", "contrasts", "tags"}
        missing = required.difference(capability)
        if missing:
            raise ValueError(
                f"Capability {capability.get('id')} is missing fields: {sorted(missing)}"
            )
        targets = capability["target_interfaces"]
        if not targets:
            raise ValueError(f"Capability {capability['id']} has no target interface")
        primary_count = sum(item.get("role") == "primary" for item in targets)
        if primary_count != 1:
            raise ValueError(
                f"Capability {capability['id']} must have exactly one primary interface"
            )
        for target in targets:
            if target.get("id") not in known_interfaces:
                raise ValueError(
                    f"Capability {capability['id']} references unknown interface "
                    f"{target.get('id')}"
                )
        for contrast in capability["contrasts"]:
            if contrast.get("interface_id") not in known_interfaces:
                raise ValueError(
                    f"Capability {capability['id']} contrasts unknown interface "
                    f"{contrast.get('interface_id')}"
                )
    return data


def capability_to_document(capability: Dict[str, Any]) -> str:
    """Render positive retrieval evidence for a single capability.

    Contrasts are deliberately excluded. Their negative interface names can
    otherwise pull a query toward the wrong capability in dense retrieval.
    """
    expressions = "\n".join(
        f"- {text}" for text in capability.get("expressions", []) if text
    )
    targets = capability["target_interfaces"]
    target_lines = "\n".join(
        f"- {item['id']}（{'首选' if item['role'] == 'primary' else '等价入口'}）："
        f"{item.get('reason') or capability['intent']}"
        for item in targets
    )
    tags = "、".join(capability.get("tags") or [])
    return "\n".join([
        f"计算目标：{capability['intent']}",
        "用户可能的表达：",
        expressions,
        "对应的 FEALPy 接口：",
        target_lines,
        f"检索关键词：{tags}",
    ])


def capability_to_metadata(
    capability: Dict[str, Any],
    interface_by_id: Dict[str, Dict[str, Any]],
    *,
    schema_version: str,
    dataset_version: str,
) -> Dict[str, Any]:
    """Create scalar-only Chroma metadata for retrieval and later reranking."""
    targets = capability["target_interfaces"]
    primary = next(item for item in targets if item["role"] == "primary")
    alternatives = [item["id"] for item in targets if item["role"] == "alternative"]
    primary_record = interface_by_id[primary["id"]]
    return {
        "capability_id": capability["id"],
        "intent": capability["intent"],
        "primary_interface": primary["id"],
        "alternative_interfaces": json.dumps(alternatives, ensure_ascii=False),
        "all_interfaces": json.dumps([item["id"] for item in targets], ensure_ascii=False),
        "category": primary_record.get("category") or "other",
        "source": primary_record.get("source") or "",
        "tags": json.dumps(capability.get("tags") or [], ensure_ascii=False),
        "contrasts": json.dumps(capability.get("contrasts") or [], ensure_ascii=False),
        "schema_version": schema_version,
        "dataset_version": dataset_version,
    }


def build_records(data: Dict[str, Any]) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """Build aligned Chroma IDs, documents and metadata lists."""
    interface_by_id = {item["id"]: item for item in data["interfaces"]}
    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    for capability in data["capabilities"]:
        ids.append(capability["id"])
        documents.append(capability_to_document(capability))
        metadatas.append(capability_to_metadata(
            capability,
            interface_by_id,
            schema_version=data["schema_version"],
            dataset_version=data["dataset_version"],
        ))
    return ids, documents, metadatas


def batched(items: List[Any], size: int) -> Iterable[List[Any]]:
    for start in range(0, len(items), size):
        yield items[start:start + size]

