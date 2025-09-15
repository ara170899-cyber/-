"""Console application for practising English with daily words and a chat bot."""

from __future__ import annotations

import sys
from textwrap import fill

from .chatbot import ChatBot, EXIT_KEYWORDS
from .daily_words import DailyWordTrainer
from .rewards import Reward, RewardEngine
from .storage import ProgressStorage


def format_rewards(rewards: list[Reward]) -> str:
    if not rewards:
        return "Новых наград нет пока. Продолжайте заниматься!"
    parts = [f"🏆 {reward.name} — {reward.description}" for reward in rewards]
    return "\n".join(parts)


def show_daily_words(trainer: DailyWordTrainer) -> None:
    words, points, new_rewards = trainer.get_today_words()
    if not words:
        print("Сегодня слова не найдены. Проверьте файл со словарём.")
        return

    print("\nСлова дня:")
    for idx, word in enumerate(words, 1):
        print(f" {idx}. {word['word']} — {word['translation']}")
        print(f"    Пример: {word['example']}")

    if points:
        print(f"\nВы получили {points} очков за новые слова!")
    if new_rewards:
        print("Новые награды:")
        print(format_rewards(new_rewards))

    progress = trainer.storage.load()
    print("\nТекущий прогресс:")
    print(f" Очки: {progress['points']}")
    print(f" Серия дней: {progress['streak']}")
    print(f" Выучено слов: {len(progress.get('learned_words', []))}")


def choose_topic(chatbot: ChatBot) -> str | None:
    topics = chatbot.topics()
    print("\nТемы для разговора:")
    for index, topic in enumerate(topics, 1):
        print(f" {index}. {topic.title}")
        print(f"    {fill(topic.intro, width=70)}")
        if topic.hints:
            print("    Подсказки:")
            for hint in topic.hints:
                print(f"     - {hint}")

    choice = input("\nВыберите номер темы (или нажмите Enter, чтобы вернуться): ").strip()
    if not choice:
        return None
    if not choice.isdigit() or not (1 <= int(choice) <= len(topics)):
        print("Не удалось распознать выбор. Попробуйте снова.")
        return None
    return topics[int(choice) - 1].slug


def talk_with_bot(chatbot: ChatBot, topic_slug: str) -> None:
    print("\nЧтобы завершить разговор, напишите одно из слов: " + ", ".join(sorted(EXIT_KEYWORDS)))
    while True:
        message = input("Вы: ")
        response, points, new_rewards = chatbot.respond(topic_slug, message)
        print(f"Бот: {response}")
        lowered = message.strip().lower()
        if points:
            print(f"(+{points} очков)")
        if new_rewards:
            print(format_rewards(new_rewards))
        if lowered and any(keyword in lowered for keyword in EXIT_KEYWORDS):
            break


def show_progress(storage: ProgressStorage, reward_engine: RewardEngine) -> None:
    progress = storage.load()
    print("\nВаш прогресс:")
    print(f" Очки: {progress['points']}")
    print(f" Серия дней: {progress['streak']}")
    print(f" Выучено слов: {len(progress.get('learned_words', []))}")
    if progress.get("rewards"):
        print(" Доступные награды:")
        for reward_id in progress["rewards"]:
            reward = reward_engine.get_reward(reward_id)
            if reward:
                print(f"  - {reward.name}: {reward.description}")
    else:
        print(" Пока без наград, но всё впереди!")


def main() -> int:
    storage = ProgressStorage()
    reward_engine = RewardEngine()
    trainer = DailyWordTrainer(storage=storage, reward_engine=reward_engine)
    chatbot = ChatBot(storage=storage, reward_engine=reward_engine)

    print("Добро пожаловать в тренажёр английского языка! 🎯")

    while True:
        print("\nМеню:")
        print(" 1. Слова дня")
        print(" 2. Поговорить с ботом")
        print(" 3. Посмотреть прогресс")
        print(" 4. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_daily_words(trainer)
        elif choice == "2":
            topic = choose_topic(chatbot)
            if topic:
                talk_with_bot(chatbot, topic)
        elif choice == "3":
            show_progress(storage, reward_engine)
        elif choice == "4":
            print("До встречи! Продолжайте практиковаться каждый день.")
            return 0
        else:
            print("Неизвестная команда. Введите цифру из меню.")


if __name__ == "__main__":
    sys.exit(main())

