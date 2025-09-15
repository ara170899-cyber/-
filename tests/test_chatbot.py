from pathlib import Path

from app.chatbot import ChatBot
from app.rewards import RewardEngine
from app.storage import ProgressStorage


def create_chatbot(tmp_path):
    storage = ProgressStorage(tmp_path / "progress.json")
    reward_engine = RewardEngine()
    conversation_path = Path(__file__).resolve().parents[1] / "app" / "data" / "conversations.json"
    bot = ChatBot(storage=storage, reward_engine=reward_engine, conversation_path=conversation_path)
    return bot, storage


def test_chatbot_keyword_response_and_points(tmp_path):
    bot, storage = create_chatbot(tmp_path)

    response, points, rewards = bot.respond("travel", "I love the beach in summer")
    assert "beach" in response.lower()
    assert points == bot.points_per_message
    assert storage.load()["points"] == points
    assert not rewards  # Not enough points for a new reward yet

    response_exit, exit_points, exit_rewards = bot.respond("travel", "bye")
    assert "thanks" in response_exit.lower()
    assert exit_points == 0
    assert not exit_rewards

