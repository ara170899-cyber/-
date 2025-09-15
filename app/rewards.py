"""Gamification helpers and predefined rewards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class Reward:
    """Represents a reward that can be unlocked by the learner."""

    id: str
    name: str
    description: str
    metric: str
    threshold: int


DEFAULT_REWARDS: List[Reward] = [
    Reward(
        id="points_50",
        name="Первый рывок",
        description="Вы набрали 50 очков и получили мешочек виртуальных конфет!",
        metric="points",
        threshold=50,
    ),
    Reward(
        id="streak_3",
        name="Упорный ученик",
        description="3 дня подряд вы изучаете слова — держите стикеры мотивации!",
        metric="streak",
        threshold=3,
    ),
    Reward(
        id="words_40",
        name="Словарный мастер",
        description="40 выученных слов — пора получить новую обложку для дневника!",
        metric="words",
        threshold=40,
    ),
]


class RewardEngine:
    """Unlocks rewards based on learner progress."""

    def __init__(self, rewards: Iterable[Reward] | None = None) -> None:
        self._rewards = list(rewards or DEFAULT_REWARDS)

    def all_rewards(self) -> List[Reward]:
        """Return a copy of the configured rewards."""
        return list(self._rewards)

    def get_reward(self, reward_id: str) -> Reward | None:
        for reward in self._rewards:
            if reward.id == reward_id:
                return reward
        return None

    def evaluate(self, progress: Dict[str, int | str | list]) -> List[Reward]:
        """Return rewards unlocked by the current progress state."""
        unlocked: List[Reward] = []
        obtained = set(progress.get("rewards", []))

        for reward in self._rewards:
            if reward.id in obtained:
                continue

            if reward.metric == "points" and progress.get("points", 0) >= reward.threshold:
                unlocked.append(reward)
            elif reward.metric == "streak" and progress.get("streak", 0) >= reward.threshold:
                unlocked.append(reward)
            elif reward.metric == "words" and len(progress.get("learned_words", [])) >= reward.threshold:
                unlocked.append(reward)

        if unlocked:
            obtained.update(r.id for r in unlocked)
            progress["rewards"] = list(obtained)

        return unlocked

