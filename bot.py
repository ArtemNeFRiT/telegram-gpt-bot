import logging

from telegram import Update, Bot
from telegram.constants import ChatType
from telegram.ext import CommandHandler, MessageHandler, Application, ContextTypes, filters

from features.ai.open_ai import OpenAIClient
from features.analytics.events import EventsTracker
from features.statistic.statistic_provider import StatisticProvider
from features.telegram.telegram_bot import TelegramBot
from features.welcome.concierge import Concierge
from security.guard import Guard

logger = logging.getLogger(__name__)
guard = Guard()
open_ai = OpenAIClient(guard)
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
            events_tracker.user_not_found(user_name)
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
    ai_response = open_ai.get_response_for_new_message(user_name, user_message)
    statistic_provider.save_statistic(user_name, ai_response)
    events_tracker.save_ai_response_event(user_name, ai_response)
    await telegram_bot.post_message_to_telegram_chat(chat_id, ai_response.assistant_message, bot)


async def reply_in_group(chat_id: int, message_id: int, user_name: str, user_message: str, bot: Bot):
    ai_response = open_ai.get_response_for_new_group_message(chat_id, user_name, user_message)
    events_tracker.save_ai_response_event(user_name, ai_response)
    await telegram_bot.reply_message_to_telegram_chat(chat_id, message_id, ai_response.assistant_message, bot)


async def clear_private_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.name
    open_ai.clear_user_messages(user_name)
    events_tracker.clear_context(user_name)
    await telegram_bot.post_context_cleared_message(update.effective_chat.id, context.bot)


async def clear_group_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.name
    if guard.is_user_admin(user_name):
        chat_id_str = update.message.text.replace("/clear_group_context", "").strip()
        user_name = update.effective_user.name
        open_ai.clear_user_messages(chat_id_str)
        events_tracker.clear_group_context(user_name, chat_id_str)
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
                f"prompt_tokens: {user.prompt_tokens}"
                f"completion_tokens: {user.completion_tokens}"
                f"total_tokens: {user.total_tokens}"
            )
    else:
        await telegram_bot.post_not_administrator_message(update.effective_chat.id, context.bot)


async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.name
    user_message = update.message.text
    chat_type = update.effective_message.chat.type

    prompt = user_message.replace("/generate_image", "").strip()

    if guard.is_user_available(user_name):
        generated_image_url = open_ai.generate_ai_response_with_image(prompt)
        await telegram_bot.post_message_to_telegram_chat(chat_id, generated_image_url, context.bot)
    else:
        events_tracker.user_not_found(user_name)
        await telegram_bot.post_not_allowed_message(chat_id, context.bot)


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
    application.add_handler(CommandHandler("generate_image", generate_image))

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_welcome_message))
    application.add_handler(MessageHandler(filters.TEXT, reply))
    application.run_polling()


if __name__ == '__main__':
    main()
