"""Compatibility facade for the current v02 vector knowledge base.

New code may import :mod:`vector_kb_v02` directly. This module keeps the
historic import path from silently selecting the archived v01 database.
"""

from vector_kb_v02 import (  # noqa: F401
    DEFAULT_COLLECTION,
    DEFAULT_DATA_FILE,
    DEFAULT_DB_DIR,
    DEFAULT_MODEL_DIR,
    DEFAULT_STORE_DIR,
    PROJECT_DIR,
    REPO_DIR,
    batched,
    build_records,
    capability_to_document,
    capability_to_metadata,
    load_dataset,
)


def load_interfaces(path=DEFAULT_DATA_FILE):
    """Return the v02 interface fact table for legacy read-only callers."""
    return load_dataset(path)["interfaces"]

