"""Bounded in-memory conversation state for follow-up questions."""

from __future__ import annotations

from collections import deque
from dataclasses import asdict
from typing import Deque, Dict, List, Optional

from schemas import AgentAnswer, ConversationTurn, QueryIntent


class ConversationMemory:
    def __init__(self, max_turns: int = 6) -> None:
        self.max_turns = max_turns
        self._sessions: Dict[str, Deque[ConversationTurn]] = {}

    def turns(self, session_id: str) -> List[ConversationTurn]:
        return list(self._sessions.get(session_id, ()))

    def context(self, session_id: str, limit: int = 3) -> List[dict]:
        turns = self.turns(session_id)[-limit:]
        return [
            {
                "user": turn.query,
                "assistant": turn.answer,
                "intent": asdict(turn.intent),
                "interfaces": turn.interface_ids,
            }
            for turn in turns
        ]

    def previous_intent(self, session_id: str) -> Optional[QueryIntent]:
        turns = self.turns(session_id)
        return turns[-1].intent if turns else None

    def add(self, session_id: str, answer: AgentAnswer) -> None:
        turns = self._sessions.setdefault(
            session_id, deque(maxlen=self.max_turns)
        )
        turns.append(
            ConversationTurn(
                query=answer.query,
                answer=answer.text,
                intent=answer.intent,
                interface_ids=[item.id for item in answer.matches],
            )
        )

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
