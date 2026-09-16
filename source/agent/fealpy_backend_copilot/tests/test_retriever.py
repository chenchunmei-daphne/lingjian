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
            "ids": [["bm.sum"]], "distances": [[0.1]],
        }
        retriever.records = {
            "bm.sum": {
                "id": "bm.sum", "full_name": "bm.sum",
                "category": "reduction", "backends": {},
            }
        }

        retriever.search(QueryIntent("求和", "sum", category="creation"))

        kwargs = retriever.collection.query.call_args.kwargs
        self.assertNotIn("where", kwargs)


if __name__ == "__main__":
    unittest.main()
