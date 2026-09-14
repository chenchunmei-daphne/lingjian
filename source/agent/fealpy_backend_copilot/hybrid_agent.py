"""Qwen + vector retrieval assistant with deterministic fallbacks."""

from __future__ import annotations

from conversation import ConversationMemory
from llm_answer_generator import LLMAnswerGenerator
from llm_client import QwenClient
from llm_intent_parser import LLMIntentParser
from retriever import FealpyRetriever
from schemas import AgentAnswer


class HybridFealpyBackendAgent:
    def __init__(
        self,
        client=None,
        intent_parser=None,
        retriever=None,
        answer_generator=None,
        memory=None,
    ) -> None:
        self.client = client or QwenClient()
        self.intent_parser = intent_parser or LLMIntentParser(self.client)
        self.retriever = retriever or FealpyRetriever()
        self.answer_generator = answer_generator or LLMAnswerGenerator(self.client)
        self.memory = memory or ConversationMemory()

    def run(
        self,
        query: str,
        top_k: int = 5,
        session_id: str = "default",
    ) -> AgentAnswer:
        history = self.memory.context(session_id)
        intent = self.intent_parser.parse(
            query,
            top_k=top_k,
            history=history,
            previous_intent=self.memory.previous_intent(session_id),
        )
        results = self.retriever.search(intent)
        answer = self.answer_generator.generate(
            query, intent, results, history=history
        )
        answer.intent_source = self.intent_parser.last_source
        answer.answer_source = self.answer_generator.last_source
        self.memory.add(session_id, answer)
        return answer

    def clear_session(self, session_id: str = "default") -> None:
        self.memory.clear(session_id)
