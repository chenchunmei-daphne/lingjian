"""Query the persistent FEALPy interface vector knowledge base."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from vector_kb import DEFAULT_COLLECTION, DEFAULT_DB_DIR, DEFAULT_MODEL_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Natural-language interface requirement")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--category",
        choices=[
            "creation", "math", "linalg", "manipulation",
            "reduction", "comparison", "dtype", "other",
        ],
    )
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_DIR)
    parser.add_argument("--collection", default=DEFAULT_COLLECTION)
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    model = SentenceTransformer(str(args.model.resolve()))
    query_embedding = model.encode(
        [args.query], normalize_embeddings=True
    ).tolist()

    client = chromadb.PersistentClient(path=str(args.db.resolve()))
    collection = client.get_collection(args.collection)
    where = {"category": args.category} if args.category else None
    result = collection.query(
        query_embeddings=query_embedding,
        n_results=min(args.top_k, collection.count()),
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    for rank, (item_id, metadata, distance) in enumerate(
        zip(result["ids"][0], result["metadatas"][0], result["distances"][0]),
        start=1,
    ):
        print(f"{rank}. {item_id}  cosine_distance={distance:.4f}")
        print(f"   NumPy:  {metadata.get('numpy_api') or '无单一对应 API'}")
        print(f"   PyTorch: {metadata.get('pytorch_api') or '无单一对应 API'}")
        print(f"   Source:  {metadata.get('source')}")


if __name__ == "__main__":
    main()
