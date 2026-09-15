"""Orchestration layer for the rule-based FEALPy backend assistant."""

from __future__ import annotations

from answer_generator import TemplateAnswerGenerator
from intent_parser import RuleBasedIntentParser
from retriever import FealpyRetriever
from schemas import AgentAnswer


class FealpyBackendAgent:
    def __init__(self) -> None:
        self.intent_parser = RuleBasedIntentParser()
        self.retriever = FealpyRetriever()
        self.answer_generator = TemplateAnswerGenerator()

    def run(self, query: str, top_k: int = 5) -> AgentAnswer:
        intent = self.intent_parser.parse(query, top_k=top_k)
        results = self.retriever.search(intent)
        return self.answer_generator.generate(query, intent, results)

