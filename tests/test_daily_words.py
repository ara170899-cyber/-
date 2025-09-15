from datetime import date
from pathlib import Path

from app.daily_words import DailyWordTrainer
from app.rewards import RewardEngine
from app.storage import ProgressStorage


def build_trainer(tmp_path):
    storage = ProgressStorage(tmp_path / "progress.json")
    reward_engine = RewardEngine()
    words_path = Path(__file__).resolve().parents[1] / "app" / "data" / "words.json"
    trainer = DailyWordTrainer(storage=storage, reward_engine=reward_engine, words_path=words_path)
    return trainer


def test_get_today_words_awards_points_and_rewards(tmp_path):
    trainer = build_trainer(tmp_path)

    words, points, rewards = trainer.get_today_words(today=date(2023, 1, 1))
    assert len(words) == trainer.words_per_day
    assert points == 10 * len(words)
    assert any(reward.id == "points_50" for reward in rewards)

    progress = trainer.storage.load()
    assert progress["last_word_date"] == "2023-01-01"
    assert progress["points"] == points

    # Repeating within the same day should not award additional points
    words_again, extra_points, extra_rewards = trainer.get_today_words(today=date(2023, 1, 1))
    assert [word["word"] for word in words_again] == [word["word"] for word in words]
    assert extra_points == 0
    assert not extra_rewards


def test_daily_word_streak_increments_and_resets(tmp_path):
    trainer = build_trainer(tmp_path)

    trainer.get_today_words(today=date(2023, 1, 1))
    trainer.get_today_words(today=date(2023, 1, 2))
    progress = trainer.storage.load()
    assert progress["streak"] == 2

    trainer.get_today_words(today=date(2023, 1, 4))
    progress = trainer.storage.load()
    assert progress["streak"] == 1

