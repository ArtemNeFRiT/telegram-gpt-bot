import logging

from telegram import Update, Bot
from telegram.constants import ChatType
from telegram.ext import CommandHandler, MessageHandler, Application, ContextTypes, filters

from features.ai.open_ai import OpenAI
from features.analytics.events import EventsTracker
from features.statistic.statistic_provider import StatisticProvider
from features.telegram.telegram_bot import TelegramBot
from features.welcome.concierge import Concierge
from security.guard import Guard

logger = logging.getLogger(__name__)
guard = Guard()
open_ai = OpenAI(guard)
telegram_bot = TelegramBot()
events_tracker = EventsTracker()
statistic_provider = StatisticProvider()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await telegram_bot.post_greetings_message(update.effective_chat.id, context.bot)


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.name
    user_message = update.message.text
    chat_type = update.effective_message.chat.type
    message_id = update.message.message_id

    is_private_message = chat_type == ChatType.PRIVATE

    if is_private_message:
        if guard.is_user_available(user_name):
            await reply_private_message(chat_id, user_name, user_message, context.bot)
        else:
            events_tracker.save_event(user_name, "пользователь не найден")
            await telegram_bot.post_not_allowed_message(chat_id, context.bot)
    else:
        is_appeal_in_group = f"@chat_gpt_ai_tg_bot " in user_message and chat_type != ChatType.PRIVATE
        user_message_stripped = user_message.replace("@chat_gpt_ai_tg_bot", "").strip()
        if is_appeal_in_group:
            if guard.is_group_available(chat_id):
                await reply_in_group(chat_id, message_id, user_name, user_message_stripped, context.bot)
            else:
                await telegram_bot.post_group_not_allowed_message(chat_id, context.bot)


async def reply_private_message(chat_id: int, user_name: str, user_message: str, bot: Bot):
    result = open_ai.get_response_for_new_message(user_name, user_message)
    words_count = count_words(result)
    statistic_provider.save_statistic(user_name, words_count)
    events_tracker.save_event(user_name, "получил ответ. Кол-во слов: " + str(words_count))
    await telegram_bot.post_message_to_telegram_chat(chat_id, result, bot)


async def reply_in_group(chat_id: int, message_id: int, user_name: str, user_message: str, bot: Bot):
    result = open_ai.get_response_for_new_group_message(chat_id, user_name, user_message)
    words_count = count_words(result)
    events_tracker.save_event(user_name, "получил ответ в группе. Кол-во слов: " + str(words_count))
    await telegram_bot.reply_message_to_telegram_chat(chat_id, message_id, result, bot)


def count_words(sentence):
    words = sentence.split()
    return len(words)


async def clear_private_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.name
    open_ai.clear_user_messages(user_name)
    events_tracker.save_event(user_name, "очистил контекст")
    await telegram_bot.post_context_cleared_message(update.effective_chat.id, context.bot)


async def clear_group_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.name
    if guard.is_user_admin(user_name):
        chat_id_str = update.message.text.replace("/clear_group_context", "").strip()
        user_name = update.effective_user.name
        open_ai.clear_user_messages(chat_id_str)
        events_tracker.save_event(user_name, "очистил контекст группы " + chat_id_str)
        await telegram_bot.post_group_context_cleared_message(update.effective_chat.id, context.bot)
    else:
        await telegram_bot.post_not_administrator_message(update.effective_chat.id, context.bot)


async def post_month_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.name
    if guard.is_user_admin(user_name):
        top_users_count = 3
        users = statistic_provider.find_users_with_max_usage(top_users_count)
        for user in users:
            logger.info(
                f"user: {user.user_name}, "
                f"calls: {user.calls},"
                f" completion_words_count: {user.completion_words_count}"
            )
    else:
        await telegram_bot.post_not_administrator_message(update.effective_chat.id, context.bot)


async def new_member_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_member_first_name = update.message.new_chat_members[0].first_name
    new_member = update.message.new_chat_members[0].name
    chat_id = update.effective_chat.id
    concierge = Concierge(telegram_bot, open_ai)

    bot_added_to_group_event = "@chat_gpt_ai_tg_bot" == new_member
    if bot_added_to_group_event:
        if guard.is_group_available(chat_id):
            await concierge.say_hello(chat_id, context.bot)
        else:
            await telegram_bot.post_group_not_allowed_message(chat_id, context.bot)
    else:
        if guard.is_group_available(chat_id):
            await concierge.welcome_new_user(chat_id, context.bot, new_member_first_name)
        else:
            await telegram_bot.post_group_not_allowed_message(chat_id, context.bot)


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting ChatGPTBot")

    application = Application.builder().token(TelegramBot.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear_context", clear_private_context))
    application.add_handler(CommandHandler("clear_group_context", clear_group_context))
    application.add_handler(CommandHandler("post_month_statistics", post_month_statistics))

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_welcome_message))
    application.add_handler(MessageHandler(filters.TEXT, reply))
    application.run_polling()


if __name__ == '__main__':
    main()
