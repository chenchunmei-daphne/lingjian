from hybrid_agent import HybridFealpyBackendAgent


def main():
    agent = HybridFealpyBackendAgent()

    questions = [
        "PyTorch 后端如何在 GPU 上创建 3×4 的全零张量？",
        # "FEALPy 如何求解线性方程组 Ax=b？",
        # "怎样创建服从标准正态分布的随机张量？",
    ]

    for question in questions:
        answer = agent.run(question, top_k=3)

        print("=" * 80)
        print("用户问题：", question)
        print(
            f"运行状态：intent={answer.intent_source}, "
            f"answer={answer.answer_source}"
        )
        print()
        print(answer.text)


if __name__ == "__main__":
    main()