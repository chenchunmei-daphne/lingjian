"""Command-line entry point for the rule-based FEALPy assistant."""

from __future__ import annotations

import argparse
import sys

from agent import FealpyBackendAgent


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="FEALPy interface question")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    agent = FealpyBackendAgent()
    answer = agent.run(args.query, top_k=args.top_k)
    print(answer.text)


if __name__ == "__main__":
    main()
