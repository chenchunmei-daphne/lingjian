from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from retriever import FealpyRetriever
from schemas import QueryIntent


class RetrieverFilteringTests(unittest.TestCase):
    def test_category_is_soft_ranking_signal_not_chroma_filter(self):
        retriever = FealpyRetriever.__new__(FealpyRetriever)
        retriever.model = Mock()
        retriever.model.encode.return_value.tolist.return_value = [[0.1, 0.2]]
        retriever.collection = Mock()
        retriever.collection.count.return_value = 1
        retriever.collection.query.return_value = {
            "ids": [["interface.sum"]], "distances": [[0.1]],
        }
        retriever.records = {
            "bm.sum": {
                "id": "bm.sum", "name": "sum",
                "summary": "计算张量元素之和",
                "category": "reduction", "source": "source.py:L1",
            }
        }
        retriever.capabilities = {
            "interface.sum": {
                "id": "interface.sum",
                "intent": "计算张量元素之和",
                "expressions": ["求和"],
                "target_interfaces": [{
                    "id": "bm.sum", "role": "primary", "reason": "计算元素之和"
                }],
                "contrasts": [],
                "tags": ["求和", "sum"],
            }
        }

        results = retriever.search(
            QueryIntent("求和", "sum", category="creation")
        )

        kwargs = retriever.collection.query.call_args.kwargs
        self.assertNotIn("where", kwargs)
        self.assertEqual(results[0].id, "bm.sum")

    def test_equivalent_interfaces_are_expanded_from_one_capability(self):
        retriever = FealpyRetriever.__new__(FealpyRetriever)
        retriever.model = Mock()
        retriever.model.encode.return_value.tolist.return_value = [[0.1, 0.2]]
        retriever.collection = Mock()
        retriever.collection.count.return_value = 1
        retriever.collection.query.return_value = {
            "ids": [["interface.matmul"]], "distances": [[0.1]],
        }
        retriever.records = {
            api: {
                "id": api, "name": "matmul", "summary": "执行矩阵乘法",
                "category": "linalg", "source": "source.py:L1",
            }
            for api in ("bm.matmul", "bm.linalg.matmul")
        }
        retriever.capabilities = {
            "interface.matmul": {
                "id": "interface.matmul", "intent": "执行矩阵乘法",
                "expressions": ["两个矩阵相乘"], "tags": ["矩阵乘法"],
                "contrasts": [],
                "target_interfaces": [
                    {"id": "bm.matmul", "role": "primary", "reason": "矩阵乘法"},
                    {"id": "bm.linalg.matmul", "role": "alternative", "reason": "等价入口"},
                ],
            }
        }

        results = retriever.search(QueryIntent("矩阵乘法", "matmul", top_k=2))

        self.assertEqual(
            [result.id for result in results],
            ["bm.matmul", "bm.linalg.matmul"],
        )


if __name__ == "__main__":
    unittest.main()
