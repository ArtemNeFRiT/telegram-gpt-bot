import logging
import os
from datetime import datetime

from features.ai.model.ai_response import AIResponse

logger = logging.getLogger(__name__)


class EventsTracker:
    _EVENTS_FILE_PATH = "analytics/events.txt"
    _DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    _FOLDER_NAME = "analytics"

    def _save_event(self, user: str, event: str):
        if not os.path.exists(self._FOLDER_NAME):
            os.makedirs(self._FOLDER_NAME)

        date_time = datetime.now()
        current_datetime_string = date_time.strftime(self._DATE_FORMAT)

        log_event = current_datetime_string + " user: " + user + ", event: " + event + '\n'
        logger.info(log_event)

        with open(self._EVENTS_FILE_PATH, 'a') as file:
            file.write(log_event)

    def save_ai_response_event(self, user_name: str, ai_response: AIResponse):
        prompt_tokens = ai_response.usage.prompt_tokens
        completion_tokens = ai_response.usage.completion_tokens
        total_tokens = ai_response.usage.total_tokens
        event = f"Обращение, prompt: {prompt_tokens}, completion: {completion_tokens}, total: {total_tokens}"
        self._save_event(user_name, event)

    def user_not_found(self, user_name: str):
        event = f"пользователь {user_name} не найден"
        self._save_event(user_name, event)

    def clear_context(self, user_name: str):
        event = "очистил контекст"
        self._save_event(user_name, event)

    def clear_group_context(self, user_name: str, chat_id_str: str):
        event = "очистил контекст группы " + chat_id_str
        self._save_event(user_name, event)
