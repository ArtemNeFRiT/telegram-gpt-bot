from telegram import Bot

from features.ai.open_ai import OpenAIClient
from features.telegram.telegram_bot import TelegramBot


class Concierge:

    def __init__(self, telegram_bot: TelegramBot, open_ai: OpenAIClient):
        self.telegram_bot = telegram_bot
        self.open_ai = open_ai

    async def welcome_new_user(self, chat_id: int, bot: Bot, user: str):
        prompt = self._create_welcome_prompt(user)
        result = self.open_ai.get_response_for_new_group_message(chat_id, "", prompt)
        await self.telegram_bot.post_message_to_telegram_chat(chat_id, result.assistant_message, bot)

    async def say_hello(self, chat_id: int, bot: Bot):
        prompt = self._create_hello_prompt()
        result = self.open_ai.get_response_for_new_group_message(chat_id, "", prompt)
        await self.telegram_bot.post_message_to_telegram_chat(chat_id, result.assistant_message, bot)

    def _create_hello_prompt(self) -> str:
        return "Представься."

    def _create_welcome_prompt(self, user) -> str:
        return "Придумай небольшое приветственное сообщение для нового пользователя чата - " + user
