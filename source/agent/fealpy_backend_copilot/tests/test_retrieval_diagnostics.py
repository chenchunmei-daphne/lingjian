from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from retrieval_diagnostics import _gold_rank, _metrics, _query_text
from schemas import QueryIntent


class RetrievalDiagnosticHelpersTests(unittest.TestCase):
    def test_gold_rank(self):
        self.assertEqual(_gold_rank(["bm.sum"], ["bm.max", "bm.sum"]), 2)
        self.assertIsNone(_gold_rank(["bm.sum"], ["bm.max"]))

    def test_metrics(self):
        metrics = _metrics([1, 2, None])
        self.assertAlmostEqual(metrics["recall_at_1"], 1 / 3, places=6)
        self.assertAlmostEqual(metrics["recall_at_5"], 2 / 3, places=6)
        self.assertEqual(metrics["mean_rank_found"], 1.5)

    def test_raw_query_has_no_enrichment(self):
        intent = QueryIntent("原始问题", "sum", "reduction")
        self.assertEqual(_query_text(intent, "raw"), "原始问题")
        self.assertIn("操作：sum", _query_text(intent, "query_operation"))


if __name__ == "__main__":
    unittest.main()
