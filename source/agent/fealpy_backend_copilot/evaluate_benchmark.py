"""Evaluate retrieval and end-to-end answers on the 55-question benchmark.

The script deliberately runs retrieval and chat as two separate stages.  This
makes it possible to tell whether a wrong answer was caused by recall or by
answer generation.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_BENCHMARK = PROJECT_DIR / "data" / "eval_questions_55.json"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "data" / "eval_results"
API_PATTERN = re.compile(r"(?<![\w.])bm\.[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*")
RECOMMENDATION_PATTERN = re.compile(
    r"(?:推荐接口|推荐使用|建议使用|建议接口)[^\n]{0,40}?"
    r"(bm\.[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)"
)
NON_ANSWER_APIS = {"bm.set_backend", "bm.get_current_backend"}


def normalize_api(value: str) -> str:
    """Normalize formatting without making fuzzy correctness judgments."""
    return value.strip().strip("`'\".,;:()[]{}")


def extract_answer_api(text: str) -> Optional[str]:
    """Return the first substantive bm API named by the final answer.

    Infrastructure calls such as ``bm.set_backend`` are ignored unless they are
    the only API in the answer.  Using the first recommendation avoids counting
    a gold API that appears merely in an alternatives list as a correct answer.
    """
    recommendation = RECOMMENDATION_PATTERN.search(text or "")
    if recommendation:
        return normalize_api(recommendation.group(1))
    found = [normalize_api(item) for item in API_PATTERN.findall(text or "")]
    substantive = [item for item in found if item not in NON_ANSWER_APIS]
    return (substantive or found or [None])[0]


def _load_benchmark(path: Path) -> List[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise ValueError("Benchmark must be a non-empty JSON array")
    required = {"id", "query", "expected_api"}
    seen = set()
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict) or not required.issubset(row):
            raise ValueError(f"Benchmark row {index} is missing {sorted(required)}")
        if row["id"] in seen:
            raise ValueError(f"Duplicate benchmark id: {row['id']}")
        seen.add(row["id"])
        if not isinstance(row["expected_api"], list) or not row["expected_api"]:
            raise ValueError(f"{row['id']}: expected_api must be a non-empty list")
    return rows


def _result_dict(result: Any, rank: int) -> dict:
    record = result.record
    return {
        "rank": rank,
        "id": result.id,
        "full_name": record.get("full_name") or result.id,
        "category": record.get("category"),
        "score": round(float(result.score), 8),
        "distance": round(float(result.distance), 8),
    }


def _hit_rank(expected: Iterable[str], retrieved: Sequence[dict]) -> Optional[int]:
    gold = {normalize_api(item) for item in expected}
    for item in retrieved:
        names = {normalize_api(str(item.get("id") or "")),
                 normalize_api(str(item.get("full_name") or ""))}
        if gold & names:
            return int(item["rank"])
    return None


def _failure_type(retrieval_hit_rank: Optional[int], answer_correct: bool,
                  error: Optional[str]) -> Optional[str]:
    if error:
        return "pipeline_error"
    if answer_correct:
        return None
    if retrieval_hit_rank is None:
        return "retrieval_miss"
    return "answer_error_after_retrieval_hit"


def summarize(details: Sequence[dict], top_k: int) -> dict:
    denominator = len(details)

    def slice_metrics(items: Sequence[dict]) -> dict:
        total = len(items)
        return {
            "total": total,
            f"recall_at_{top_k}": round(
                sum(item["retrieval_hit_rank"] is not None for item in items) / total, 6
            ),
            "answer_accuracy": round(
                sum(item["answer_correct"] for item in items) / total, 6
            ),
        }

    return {
        "total": denominator,
        **{
            f"recall_at_{k}": sum(
                bool(item["recall_at"][str(k)]) for item in details
            ) / denominator
            for k in range(1, top_k + 1)
        },
        "answer_accuracy": sum(item["answer_correct"] for item in details) / denominator,
        "answer_correct_count": sum(item["answer_correct"] for item in details),
        "failure_counts": {
            name: sum(item["failure_type"] == name for item in details)
            for name in (
                "retrieval_miss", "answer_error_after_retrieval_hit", "pipeline_error"
            )
        },
        "by_category": {
            value: slice_metrics([item for item in details
                                  if item["expected_category"] == value])
            for value in sorted({item["expected_category"] for item in details})
        },
        "by_difficulty": {
            value: slice_metrics([item for item in details
                                  if item["difficulty"] == value])
            for value in sorted({item["difficulty"] for item in details})
        },
        "mean_retrieval_seconds": round(
            sum(item["retrieval_seconds"] for item in details) / denominator, 4),
        "mean_chat_seconds": round(
            sum(item["chat_seconds"] for item in details) / denominator, 4),
    }


def evaluate(rows: Sequence[dict], agent: Any, top_k: int = 5,
             progress: bool = True) -> tuple[dict, List[dict]]:
    details: List[dict] = []
    for index, row in enumerate(rows, 1):
        query = row["query"]
        expected = [normalize_api(item) for item in row["expected_api"]]
        retrieval: List[dict] = []
        answer_text = ""
        answer_api = None
        intent_source = None
        answer_source = None
        elapsed_retrieval = 0.0
        elapsed_chat = 0.0
        error = None
        try:
            started = time.perf_counter()
            intent = agent.intent_parser.parse(query, top_k=top_k)
            retrieval = [
                _result_dict(item, rank)
                for rank, item in enumerate(agent.retriever.search(intent), 1)
            ]
            elapsed_retrieval = time.perf_counter() - started

            # A unique session makes all 55 examples independent single turns.
            started = time.perf_counter()
            answer = agent.run(
                query, top_k=top_k,
                session_id=f"benchmark-{row['id']}-{uuid.uuid4().hex}",
            )
            elapsed_chat = time.perf_counter() - started
            answer_text = answer.text
            answer_api = extract_answer_api(answer_text)
            intent_source = answer.intent_source
            answer_source = answer.answer_source
        except Exception as exc:  # retain the sample instead of losing the run
            error = f"{type(exc).__name__}: {exc}"

        hit_rank = _hit_rank(expected, retrieval)
        answer_correct = answer_api in set(expected)
        failure_type = _failure_type(hit_rank, answer_correct, error)
        details.append({
            "id": row["id"],
            "query": query,
            "expected_api": expected,
            "expected_category": row.get("expected_category"),
            "difficulty": row.get("difficulty"),
            "retrieved": retrieval,
            "retrieval_hit_rank": hit_rank,
            "recall_at": {str(k): hit_rank is not None and hit_rank <= k
                          for k in range(1, top_k + 1)},
            "answer_api": answer_api,
            "answer_correct": answer_correct,
            "answer_text": answer_text,
            "intent_source": intent_source,
            "answer_source": answer_source,
            "failure_type": failure_type,
            "error": error,
            "retrieval_seconds": round(elapsed_retrieval, 4),
            "chat_seconds": round(elapsed_chat, 4),
        })
        if progress:
            mark = "OK" if answer_correct else failure_type
            print(f"[{index:02d}/{len(rows)}] {row['id']} {mark}", flush=True)

    return summarize(details, top_k), details


def _write_outputs(output_dir: Path, summary: dict, details: Sequence[dict],
                   config: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    report = {"config": config, "summary": summary, "samples": list(details)}
    (output_dir / "evaluation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    failures = [item for item in details if item["failure_type"]]
    with (output_dir / "failures.jsonl").open("w", encoding="utf-8") as stream:
        for item in failures:
            stream.write(json.dumps(item, ensure_ascii=False) + "\n")
    with (output_dir / "samples.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as stream:
        fields = ["id", "difficulty", "expected_category", "expected_api",
                  "top1", "top2", "top3", "top4", "top5",
                  "retrieval_hit_rank", "answer_api", "answer_correct",
                  "failure_type", "intent_source", "answer_source", "error"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for item in details:
            ranked = [candidate["full_name"] for candidate in item["retrieved"]]
            writer.writerow({
                "id": item["id"], "difficulty": item["difficulty"],
                "expected_category": item["expected_category"],
                "expected_api": "|".join(item["expected_api"]),
                **{f"top{k}": ranked[k - 1] if len(ranked) >= k else ""
                   for k in range(1, 6)},
                "retrieval_hit_rank": item["retrieval_hit_rank"],
                "answer_api": item["answer_api"],
                "answer_correct": item["answer_correct"],
                "failure_type": item["failure_type"],
                "intent_source": item["intent_source"],
                "answer_source": item["answer_source"], "error": item["error"],
            })


def _build_agent(mode: str) -> Any:
    if mode == "rule":
        from agent import FealpyBackendAgent

        base = FealpyBackendAgent()

        class RuleChatAdapter:
            intent_parser = base.intent_parser
            retriever = base.retriever

            @staticmethod
            def run(query: str, top_k: int, session_id: str):
                del session_id
                return base.run(query, top_k=top_k)

        return RuleChatAdapter()
    from hybrid_agent import HybridFealpyBackendAgent
    return HybridFealpyBackendAgent()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--mode", choices=("hybrid", "rule"), default="hybrid")
    parser.add_argument("--top-k", type=int, default=5, choices=range(1, 6))
    parser.add_argument("--limit", type=int, help="Run only the first N cases (smoke test)")
    args = parser.parse_args()
    rows = _load_benchmark(args.benchmark)
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit must be positive")
        rows = rows[:args.limit]
    agent = _build_agent(args.mode)
    summary, details = evaluate(rows, agent, top_k=args.top_k)
    config = {"benchmark": str(args.benchmark.resolve()), "mode": args.mode,
              "top_k": args.top_k, "limit": args.limit}
    _write_outputs(args.output_dir, summary, details, config)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Outputs: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
