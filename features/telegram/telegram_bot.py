from telegram import Bot

GREETING_MESSAGE = "Привет! Я OpenAI бот. Используйте мои навыки для помощи в решении задач."
NOT_ALLOWED_MESSAGE = "Извините, вас нет в списке пользователей. Для организации доступа заполните заявку: https://forms.gle/rgPQktvu5FCwpa7Q7"
GROUP_NOT_ALLOWED_MESSAGE = "Извините, не нашел данную группу в списке доступных. Для организации доступа заполните заявку: https://forms.gle/MU7JKF9tGKW272k6A"
NOT_ADMINISTRATOR_MESSAGE = "Извините, на нашел вас в списке администраторов"
CLEARED_CONTEXT_MESSAGE = "Контекст очищен. Начинаем с чистого листа."
CLEARED_GROUP_CONTEXT_MESSAGE = "Я месяцами изучал участников этого чата..."


class TelegramBot:
    _TELEGRAM_MAX_MESSAGE_LENGTH = 4096
    TELEGRAM_BOT_TOKEN = ""

    def __init__(self):
        self.token = self.TELEGRAM_BOT_TOKEN

    async def post_message_to_telegram_chat(self, chat_id: int, message: str, bot: Bot, disable_notification=False):
        for i in range(0, len(message), self._TELEGRAM_MAX_MESSAGE_LENGTH):
            chunk = message[i:i + self._TELEGRAM_MAX_MESSAGE_LENGTH]
            await bot.send_message(chat_id=chat_id, text=chunk, disable_notification=disable_notification)

    async def post_greetings_message(self, chat_id: int, bot: Bot):
        await self.post_message_to_telegram_chat(chat_id, GREETING_MESSAGE, bot)

    async def post_not_allowed_message(self, chat_id: int, bot: Bot):
        await self.post_message_to_telegram_chat(chat_id, NOT_ALLOWED_MESSAGE, bot)

    async def post_group_not_allowed_message(self, chat_id: int, bot: Bot):
        await self.post_message_to_telegram_chat(chat_id, GROUP_NOT_ALLOWED_MESSAGE, bot)

    async def post_context_cleared_message(self, chat_id: int, bot: Bot):
        await self.post_message_to_telegram_chat(chat_id, CLEARED_CONTEXT_MESSAGE, bot)

    async def post_group_context_cleared_message(self, chat_id: int, bot: Bot):
        await self.post_message_to_telegram_chat(chat_id, CLEARED_GROUP_CONTEXT_MESSAGE, bot)

    async def post_not_administrator_message(self, chat_id: int, bot: Bot):
        await self.post_message_to_telegram_chat(chat_id, NOT_ALLOWED_MESSAGE, bot)
