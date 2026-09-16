"""Run retrieval ablations and attribute benchmark recall failures by stage."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from evaluate_benchmark import DEFAULT_BENCHMARK, _load_benchmark, normalize_api
from intent_parser import RuleBasedIntentParser
from retriever import FealpyRetriever
from schemas import QueryIntent
from vector_kb import DEFAULT_DATA_FILE


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "data" / "eval_results" / "retrieval_diagnostics"
RANK_CUTOFFS = (1, 5, 10, 20, 30)


def _query_text(intent: QueryIntent, variant: str) -> str:
    if variant == "raw":
        return intent.original_query
    if variant == "query_operation":
        return "\n".join((intent.original_query, f"操作：{intent.operation}"))
    if variant == "query_category":
        return "\n".join((intent.original_query, f"分类：{intent.category}"))
    if variant == "complete":
        return FealpyRetriever._query_text(intent)
    raise ValueError(f"Unknown query variant: {variant}")


def _gold_rank(expected: Iterable[str], ids: Sequence[str]) -> Optional[int]:
    gold = {normalize_api(item) for item in expected}
    for rank, item_id in enumerate(ids, 1):
        record_name = normalize_api(item_id)
        if record_name in gold:
            return rank
    return None


def _metrics(ranks: Sequence[Optional[int]]) -> dict:
    total = len(ranks)
    found = [rank for rank in ranks if rank is not None]
    return {
        "total": total,
        **{f"recall_at_{k}": round(sum(rank is not None and rank <= k for rank in ranks) / total, 6)
           for k in RANK_CUTOFFS},
        "mrr": round(sum(1.0 / rank if rank else 0.0 for rank in ranks) / total, 6),
        "mean_rank_found": round(sum(found) / len(found), 4) if found else None,
        "not_found_in_collection": sum(rank is None for rank in ranks),
    }


class DiagnosticRunner:
    def __init__(self) -> None:
        self.retriever = FealpyRetriever()
        self.parser = RuleBasedIntentParser()
        self.collection_count = self.retriever.collection.count()

    def _vector_results(self, texts: Sequence[str], categories: Sequence[Optional[str]]) -> List[List[dict]]:
        embeddings = self.retriever.model.encode(
            list(texts), normalize_embeddings=True, show_progress_bar=True,
        ).tolist()
        output: List[Optional[List[dict]]] = [None] * len(texts)
        groups: Dict[Optional[str], List[int]] = defaultdict(list)
        for index, category in enumerate(categories):
            groups[category].append(index)
        for category, indices in groups.items():
            response = self.retriever.collection.query(
                query_embeddings=[embeddings[index] for index in indices],
                n_results=self.collection_count,
                where={"category": category} if category else None,
                include=["distances"],
            )
            for position, index in enumerate(indices):
                output[index] = [
                    {"id": item_id, "distance": float(distance)}
                    for item_id, distance in zip(
                        response["ids"][position], response["distances"][position]
                    )
                ]
        return [items or [] for items in output]

    def run(self, rows: Sequence[dict]) -> tuple[dict, List[dict]]:
        intents = [self.parser.parse(row["query"], top_k=30) for row in rows]
        specs = {
            "raw_no_filter": ("raw", [None] * len(rows)),
            "query_operation_no_filter": ("query_operation", [None] * len(rows)),
            "query_category_no_filter": ("query_category", [None] * len(rows)),
            "complete_no_filter": ("complete", [None] * len(rows)),
            "complete_current_filter": ("complete", [intent.category for intent in intents]),
            "complete_oracle_filter": ("complete", [row.get("expected_category") for row in rows]),
        }
        all_results: Dict[str, List[List[dict]]] = {}
        for name, (variant, categories) in specs.items():
            print(f"Embedding/querying: {name}", flush=True)
            all_results[name] = self._vector_results(
                [_query_text(intent, variant) for intent in intents], categories
            )

        details = []
        for index, (row, intent) in enumerate(zip(rows, intents)):
            experiments = {}
            for name, vector_items_by_row in all_results.items():
                vector_items = vector_items_by_row[index]
                vector_ids = [item["id"] for item in vector_items]
                scored = []
                for item in vector_items:
                    record = self.retriever.records.get(item["id"])
                    if not record:
                        continue
                    score = 1.0 - item["distance"]
                    score += self.retriever._lexical_bonus(intent, record)
                    if intent.category == record.get("category"):
                        score += 0.08
                    if record.get("deprecated"):
                        score -= 0.2
                    if record.get("doc_quality") == "missing":
                        score -= 0.03
                    scored.append((item["id"], score))
                scored.sort(key=lambda value: value[1], reverse=True)
                reranked_ids = [item_id for item_id, _ in scored]
                experiments[name] = {
                    "vector_rank": _gold_rank(row["expected_api"], vector_ids),
                    "reranked_rank": _gold_rank(row["expected_api"], reranked_ids),
                    "vector_top5": vector_ids[:5],
                    "reranked_top5": reranked_ids[:5],
                }

            current = experiments["complete_current_filter"]
            no_filter = experiments["complete_no_filter"]
            oracle = experiments["complete_oracle_filter"]
            raw = experiments["raw_no_filter"]
            original_miss = current["reranked_rank"] is None or current["reranked_rank"] > 5
            signals = []
            if intent.category != row.get("expected_category"):
                signals.append("intent_category_wrong_or_missing")
            if ((current["reranked_rank"] is None and no_filter["reranked_rank"] is not None)
                    or ((current["reranked_rank"] or math.inf) > 5
                        and (no_filter["reranked_rank"] or math.inf) <= 5)):
                signals.append("hard_filter_blocks_gold")
            if ((current["reranked_rank"] or math.inf) > 5
                    and (oracle["reranked_rank"] or math.inf) <= 5):
                signals.append("oracle_category_recovers_top5")
            if ((no_filter["vector_rank"] or math.inf) <= 5
                    and (no_filter["reranked_rank"] or math.inf) > 5):
                signals.append("reranker_harms_top5")
            elif ((no_filter["vector_rank"] or math.inf) <= 30
                  and (no_filter["reranked_rank"] or math.inf) > 5):
                signals.append("reranker_fails_to_promote_candidate")
            if (no_filter["vector_rank"] or math.inf) > 30:
                signals.append("vector_gold_outside_initial_30")
            if ((raw["vector_rank"] or math.inf) <= 5
                    < (no_filter["vector_rank"] or math.inf)):
                signals.append("query_enrichment_harms_vector_rank")

            if original_miss and (oracle["reranked_rank"] or math.inf) <= 5:
                root_cause = (
                    "missing_category_no_narrowing"
                    if intent.category is None else "wrong_category_hard_filter"
                )
            elif original_miss:
                root_cause = "vector_representation_or_base_ranking"
            else:
                root_cause = None

            details.append({
                "id": row["id"], "query": row["query"],
                "expected_api": row["expected_api"],
                "expected_category": row.get("expected_category"),
                "parsed_category": intent.category,
                "interface_hints": intent.interface_hints,
                "hint_hits_gold": any(
                    normalize_api(gold).removeprefix("bm.") in intent.interface_hints
                    for gold in row["expected_api"]
                ),
                "original_top5_miss": original_miss,
                "root_cause": root_cause,
                "diagnostic_signals": signals,
                "experiments": experiments,
            })

        experiment_metrics = {
            name: {
                "vector": _metrics([item["experiments"][name]["vector_rank"] for item in details]),
                "reranked": _metrics([item["experiments"][name]["reranked_rank"] for item in details]),
            }
            for name in specs
        }
        failures = [item for item in details if item["original_top5_miss"]]
        summary = {
            "total": len(rows),
            "original_top5_miss_count": len(failures),
            "intent": {
                "category_accuracy": round(sum(
                    item["parsed_category"] == item["expected_category"] for item in details
                ) / len(details), 6),
                "category_confusion": dict(Counter(
                    f"{item['expected_category']} -> {item['parsed_category']}" for item in details
                    if item["parsed_category"] != item["expected_category"]
                )),
                "gold_interface_hint_recall": round(sum(
                    item["hint_hits_gold"] for item in details
                ) / len(details), 6),
            },
            "experiments": experiment_metrics,
            "failure_signal_counts": dict(Counter(
                signal for item in failures for signal in item["diagnostic_signals"]
            )),
            "exclusive_failure_attribution": dict(Counter(
                item["root_cause"] for item in failures
            )),
            "current_reranker_top5_effect": {
                "harmed": sum(
                    (item["experiments"]["complete_current_filter"]["vector_rank"] or math.inf) <= 5
                    < (item["experiments"]["complete_current_filter"]["reranked_rank"] or math.inf)
                    for item in details
                ),
                "helped": sum(
                    (item["experiments"]["complete_current_filter"]["reranked_rank"] or math.inf) <= 5
                    < (item["experiments"]["complete_current_filter"]["vector_rank"] or math.inf)
                    for item in details
                ),
            },
        }
        return summary, details


def knowledge_base_audit(rows: Sequence[dict], runner: DiagnosticRunner) -> dict:
    file_ids = set(runner.retriever.records)
    collection = runner.retriever.collection.get(include=[])
    collection_ids = set(collection["ids"])
    gold_ids = {normalize_api(api) for row in rows for api in row["expected_api"]}
    category_mismatches = []
    for row in rows:
        for api in row["expected_api"]:
            record = runner.retriever.records.get(normalize_api(api))
            if record and record.get("category") != row.get("expected_category"):
                category_mismatches.append({
                    "id": row["id"], "api": api,
                    "benchmark_category": row.get("expected_category"),
                    "record_category": record.get("category"),
                })
    manifest_path = PROJECT_DIR / "vector_store" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    data_sha256 = hashlib.sha256(DEFAULT_DATA_FILE.read_bytes()).hexdigest()
    return {
        "record_count_json": len(file_ids),
        "record_count_collection": len(collection_ids),
        "gold_api_count": len(gold_ids),
        "gold_missing_from_json": sorted(gold_ids - file_ids),
        "gold_missing_from_collection": sorted(gold_ids - collection_ids),
        "json_collection_id_difference": sorted(file_ids ^ collection_ids),
        "gold_category_mismatches": category_mismatches,
        "data_sha256": data_sha256,
        "manifest_source_sha256": manifest.get("source_sha256"),
        "manifest_matches_current_data": manifest.get("source_sha256") == data_sha256,
    }


def write_outputs(output_dir: Path, summary: dict, details: Sequence[dict], audit: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "diagnostic_report.json").write_text(json.dumps(
        {"summary": summary, "knowledge_base_audit": audit, "samples": list(details)},
        ensure_ascii=False, indent=2), encoding="utf-8")
    failures = [item for item in details if item["original_top5_miss"]]
    with (output_dir / "failure_attribution.jsonl").open("w", encoding="utf-8") as stream:
        for item in failures:
            stream.write(json.dumps(item, ensure_ascii=False) + "\n")
    fields = ["id", "expected_api", "expected_category", "parsed_category",
              "root_cause", "signals"]
    experiment_names = list(summary["experiments"])
    for name in experiment_names:
        fields.extend((f"{name}_vector_rank", f"{name}_reranked_rank"))
    with (output_dir / "ablation_ranks.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for item in details:
            row = {
                "id": item["id"], "expected_api": "|".join(item["expected_api"]),
                "expected_category": item["expected_category"],
                "parsed_category": item["parsed_category"],
                "root_cause": item["root_cause"],
                "signals": "|".join(item["diagnostic_signals"]),
            }
            for name in experiment_names:
                row[f"{name}_vector_rank"] = item["experiments"][name]["vector_rank"]
                row[f"{name}_reranked_rank"] = item["experiments"][name]["reranked_rank"]
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    rows = _load_benchmark(args.benchmark)
    if args.limit:
        rows = rows[:args.limit]
    runner = DiagnosticRunner()
    summary, details = runner.run(rows)
    audit = knowledge_base_audit(rows, runner)
    write_outputs(args.output_dir, summary, details, audit)
    print(json.dumps({"summary": summary, "knowledge_base_audit": audit},
                     ensure_ascii=False, indent=2))
    print(f"Outputs: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
