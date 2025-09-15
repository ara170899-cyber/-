"""Persistence helpers for the English learning application."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

DEFAULT_PROGRESS: Dict[str, Any] = {
    "user_name": "Ученик",
    "points": 0,
    "streak": 0,
    "last_word_date": "",
    "learned_words": [],
    "daily_word_index": 0,
    "current_daily_words": [],
    "rewards": [],
}


class ProgressStorage:
    """Stores and retrieves learner progress from a JSON file."""

    def __init__(self, path: Path | str | None = None) -> None:
        base_path = Path(path) if path is not None else Path(__file__).resolve().parent / "data" / "user_progress.json"
        self.path = base_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """Return the persisted progress, falling back to defaults."""
        if not self.path.exists():
            return deepcopy(DEFAULT_PROGRESS)

        data = json.loads(self.path.read_text(encoding="utf-8"))
        merged = deepcopy(DEFAULT_PROGRESS)
        merged.update(data)
        # Ensure mutable defaults are copied and not shared
        for key in ("learned_words", "current_daily_words", "rewards"):
            merged[key] = list(merged.get(key, []))
        return merged

    def save(self, progress: Dict[str, Any]) -> None:
        """Persist the provided progress snapshot."""
        serialisable = deepcopy(progress)
        self.path.write_text(json.dumps(serialisable, ensure_ascii=False, indent=2), encoding="utf-8")

