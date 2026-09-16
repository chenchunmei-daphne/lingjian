from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from evaluate_benchmark import extract_answer_api, normalize_api


class EvaluationHelpersTests(unittest.TestCase):
    def test_extracts_recommended_api_before_alternatives(self):
        text = "推荐接口：`bm.zeros`\n其他候选：`bm.ones`"
        self.assertEqual(extract_answer_api(text), "bm.zeros")

    def test_ignores_backend_setup_call(self):
        text = "先调用 bm.set_backend('pytorch')，再用 bm.linalg.solve(A, b)。"
        self.assertEqual(extract_answer_api(text), "bm.linalg.solve")

    def test_backend_management_can_be_the_answer(self):
        self.assertEqual(extract_answer_api("使用 bm.set_backend 切换。"), "bm.set_backend")

    def test_recommendation_wins_over_alternative_for_backend_management(self):
        text = "推荐接口：`bm.get_current_backend`\n其他候选：`bm.load_backend`"
        self.assertEqual(extract_answer_api(text), "bm.get_current_backend")

    def test_normalization_only_removes_formatting(self):
        self.assertEqual(normalize_api("`bm.sum`,"), "bm.sum")


if __name__ == "__main__":
    unittest.main()
