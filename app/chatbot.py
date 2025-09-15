"""A lightweight conversational bot for practising English."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from .rewards import Reward, RewardEngine
from .storage import ProgressStorage

EXIT_KEYWORDS = {"exit", "quit", "bye", "пока", "выход"}


@dataclass
class Topic:
    slug: str
    title: str
    intro: str
    hints: List[str]
    responses: List[Dict[str, object]]
    fallback: str
    closing: str


class ChatBot:
    """Keyword based conversational assistant."""

    def __init__(
        self,
        storage: ProgressStorage,
        reward_engine: RewardEngine,
        conversation_path: Path | str | None = None,
        points_per_message: int = 3,
    ) -> None:
        self.storage = storage
        self.reward_engine = reward_engine
        self.points_per_message = points_per_message
        path = (
            Path(conversation_path)
            if conversation_path is not None
            else Path(__file__).resolve().parent / "data" / "conversations.json"
        )
        if not path.exists():
            raise FileNotFoundError(f"Файл сценариев бесед не найден: {path}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        topics = raw.get("topics") if isinstance(raw, dict) else None
        if not topics:
            raise ValueError("conversations.json должен содержать ключ topics с данными")

        self._topics: Dict[str, Topic] = {}
        for topic in topics:
            obj = Topic(
                slug=topic["slug"],
                title=topic["title"],
                intro=topic["intro"],
                hints=list(topic.get("hints", [])),
                responses=list(topic.get("responses", [])),
                fallback=topic.get("fallback", "Tell me more."),
                closing=topic.get("closing", "Talk to you later!"),
            )
            self._topics[obj.slug] = obj

    def topics(self) -> List[Topic]:
        return list(self._topics.values())

    def respond(self, topic_slug: str, message: str) -> Tuple[str, int, List[Reward]]:
        """Return a response, awarding points for active participation."""
        if topic_slug not in self._topics:
            raise ValueError(f"Неизвестная тема: {topic_slug}")

        topic = self._topics[topic_slug]
        cleaned = message.strip()
        lower_message = cleaned.lower()

        if not cleaned:
            return "Could you add a bit more detail?", 0, []

        if any(keyword in lower_message for keyword in EXIT_KEYWORDS):
            return topic.closing, 0, []

        answer = topic.fallback
        for response in topic.responses:
            keywords = [str(k).lower() for k in response.get("keywords", [])]
            if any(keyword in lower_message for keyword in keywords):
                answer = str(response.get("answer", topic.fallback))
                break

        progress = self.storage.load()
        progress["points"] = progress.get("points", 0) + self.points_per_message
        unlocked = self.reward_engine.evaluate(progress)
        self.storage.save(progress)
        return answer, self.points_per_message, unlocked

