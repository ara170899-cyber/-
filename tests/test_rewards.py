from app.rewards import RewardEngine, Reward


def test_reward_engine_unlocks_based_on_words():
    engine = RewardEngine(rewards=[
        Reward(id="words_goal", name="Champion", description="You learned many words!", metric="words", threshold=3)
    ])
    progress = {
        "points": 0,
        "streak": 0,
        "learned_words": ["apple", "book", "city"],
        "rewards": [],
    }

    unlocked = engine.evaluate(progress)
    assert len(unlocked) == 1
    assert unlocked[0].id == "words_goal"
    assert "words_goal" in progress["rewards"]

