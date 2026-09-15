"""Example: use one session for related FEALPy follow-up questions."""

from __future__ import annotations

from hybrid_agent import HybridFealpyBackendAgent


def main() -> None:
    agent = HybridFealpyBackendAgent()
    session_id = "example-user"
    questions = [
        "怎样创建一个 3×4 的全零张量？",
        "那放到 GPU 上呢？",
        "如果改成 float64 应该怎么写？",
    ]

    for question in questions:
        print(f"\n用户：{question}")
        answer = agent.run(question, top_k=3, session_id=session_id)
        print(f"助手：{answer.text}")
        print(
            f"[intent={answer.intent_source}, answer={answer.answer_source}]"
        )

    # A new topic can reuse the session, or clear it explicitly.
    agent.clear_session(session_id)


if __name__ == "__main__":
    main()
