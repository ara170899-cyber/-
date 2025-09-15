"""Daily vocabulary selection and tracking."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from .rewards import Reward, RewardEngine
from .storage import ProgressStorage


class DailyWordTrainer:
    """Provides a set of words to learn each day and updates progress."""

    def __init__(
        self,
        storage: ProgressStorage,
        reward_engine: RewardEngine,
        words_path: Path | str | None = None,
        words_per_day: int = 5,
    ) -> None:
        self.storage = storage
        self.reward_engine = reward_engine
        self.words_per_day = words_per_day
        path = Path(words_path) if words_path is not None else Path(__file__).resolve().parent / "data" / "words.json"
        if not path.exists():
            raise FileNotFoundError(f"Список слов не найден: {path}")
        self.words: List[Dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(self.words, list):
            raise ValueError("words.json должен содержать список словарей")
        self._word_lookup = {entry["word"].lower(): entry for entry in self.words}

    def get_today_words(self, today: date | None = None) -> Tuple[List[Dict[str, str]], int, List[Reward]]:
        """Return today's words, awarding points if this is a new daily session."""
        progress = self.storage.load()
        target_date = today or date.today()
        today_iso = target_date.isoformat()

        use_new_daily_set = progress.get("last_word_date") != today_iso or not progress.get("current_daily_words")

        if not self.words:
            return [], 0, []

        if use_new_daily_set:
            selection = self._select_words(progress.get("daily_word_index", 0))
            points_awarded = 10 * len(selection)

            last_date = progress.get("last_word_date")
            if last_date:
                previous = date.fromisoformat(last_date)
                if target_date - previous == timedelta(days=1):
                    progress["streak"] = progress.get("streak", 0) + 1
                else:
                    progress["streak"] = 1
            else:
                progress["streak"] = 1

            progress["last_word_date"] = today_iso
            progress["daily_word_index"] = (progress.get("daily_word_index", 0) + len(selection)) % len(self.words)
            progress["current_daily_words"] = [word["word"] for word in selection]

            learned_words = set(progress.get("learned_words", []))
            for entry in selection:
                learned_words.add(entry["word"])
            progress["learned_words"] = list(learned_words)

            progress["points"] = progress.get("points", 0) + points_awarded
            unlocked = self.reward_engine.evaluate(progress)
            self.storage.save(progress)
            return selection, points_awarded, unlocked

        # Return the existing daily set when the user revisits the same day
        words = [self._word_lookup[word.lower()] for word in progress.get("current_daily_words", []) if word.lower() in self._word_lookup]
        return words, 0, []

    def _select_words(self, start_index: int) -> List[Dict[str, str]]:
        if not self.words:
            return []
        selection: List[Dict[str, str]] = []
        for offset in range(min(self.words_per_day, len(self.words))):
            index = (start_index + offset) % len(self.words)
            selection.append(self.words[index])
        return selection

