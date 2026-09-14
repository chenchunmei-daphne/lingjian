"""Build a persistent Chroma knowledge base from all_interfaces.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from vector_kb import (
    DEFAULT_COLLECTION,
    DEFAULT_DATA_FILE,
    DEFAULT_DB_DIR,
    DEFAULT_MODEL_DIR,
    batched,
    load_interfaces,
    record_to_document,
    record_to_metadata,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_FILE)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_DIR)
    parser.add_argument("--collection", default=DEFAULT_COLLECTION)
    parser.add_argument("--batch-size", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    data_path = args.data.resolve()
    model_path = args.model.resolve()
    db_path = args.db.resolve()

    if not model_path.is_dir():
        raise FileNotFoundError(f"Embedding model directory not found: {model_path}")
    records = load_interfaces(data_path)
    documents = [record_to_document(record) for record in records]
    metadatas = [record_to_metadata(record) for record in records]
    ids = [record["id"] for record in records]

    print(f"Loading embedding model: {model_path}")
    model = SentenceTransformer(str(model_path))
    embeddings = model.encode(
        documents,
        batch_size=args.batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_path))
    try:
        client.delete_collection(args.collection)
    except Exception:
        pass
    collection = client.create_collection(
        name=args.collection,
        metadata={"hnsw:space": "cosine"},
    )

    for start in range(0, len(ids), args.batch_size):
        end = start + args.batch_size
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
            embeddings=embeddings[start:end].tolist(),
        )

    manifest = {
        "collection": args.collection,
        "record_count": collection.count(),
        "embedding_model": str(model_path),
        "embedding_dimension": int(embeddings.shape[1]),
        "normalized_embeddings": True,
        "distance_metric": "cosine",
        "source_file": str(data_path),
        "source_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = db_path.parent / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Built collection '{args.collection}' with {collection.count()} records")
    print(f"Database: {db_path}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
