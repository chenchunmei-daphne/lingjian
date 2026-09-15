"""Command-line entry point for the Qwen-powered FEALPy assistant."""

from __future__ import annotations

import argparse
import sys

from hybrid_agent import HybridFealpyBackendAgent


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="FEALPy interface question")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--session-id", default="default")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()

    agent = HybridFealpyBackendAgent()
    if args.interactive:
        query = args.query
        while query.strip().lower() not in {"exit", "quit", "退出"}:
            answer = agent.run(
                query, top_k=args.top_k, session_id=args.session_id
            )
            print(f"[intent={answer.intent_source}, answer={answer.answer_source}]")
            print(answer.text)
            query = input("\n你：")
    else:
        answer = agent.run(
            args.query, top_k=args.top_k, session_id=args.session_id
        )
        print(f"[intent={answer.intent_source}, answer={answer.answer_source}]")
        print(answer.text)


if __name__ == "__main__":
    main()
