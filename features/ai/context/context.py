import json
import logging
import os

from features.ai.model.chat_data import ChatData
from features.ai.model.usage import UsageModel
from features.ai.model.user_data import UserData
from security.guard import Guard

logger = logging.getLogger(__name__)


class Context:

    def __init__(self, guard: Guard):
        self.guard = guard

    def load_user_messages(self, user_name: str):
        file_name = f"data/{user_name}_messages.json"
        try:
            with open(file_name, "r") as file:
                user_data = json.load(file)
                messages = user_data["messages"]
                try:
                    usage = user_data["usage"]
                    usage_model = UsageModel(usage["prompt_tokens"], usage["completion_tokens"], usage["total_tokens"])
                    return UserData(user_name, messages, usage_model)
                except KeyError:
                    return UserData(user_name, messages, UsageModel(0, 0, 0))
        except FileNotFoundError:
            return UserData(user_name, [], UsageModel(0, 0, 0))

    def load_chat_data(self, chat_id: int):
        chat_id_str = str(chat_id)
        return self.load_user_messages(chat_id_str)

    def save_user_messages(self, user_data: UserData):
        self._save_data(user_data.user_name, user_data.messages, user_data.usage)

    def save_chat_data(self, data: ChatData):
        chat_id_str = str(data.chat_id)
        self._save_data(chat_id_str, data.messages, data.usage)

    def _save_data(self, user_id: str, messages, usage: UsageModel):
        data_json = {
            "user_name": user_id,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            },
            "messages": messages,
        }

        folder_name = "data"

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_name = f"data/{user_id}_messages.json"
        with open(file_name, "w") as file:
            json.dump(data_json, file)

    def clear_user_messages(self, user_name: str):
        file_name = f"data/{user_name}_messages.json"
        try:
            os.remove(file_name)
        except FileNotFoundError:
            logger.info(f"Файл {file_name} не найден")
        except Exception as e:
            logger.info(f"Ошибка при удалении файла: {e}")

    def create_system_message_for_group(self, chat_id: int):
        group = self.guard.get_group(chat_id)
        if group is None:
            return None
        else:
            return group.create_system_message()

    def create_system_message_for_private(self, telegram_alias: str):
        user = self.guard.get_user(telegram_alias)
        if user is None:
            return None
        else:
            system_message = user.create_system_message()
            logger.info(f"Пользователь {user.telegram_alias}. Системное сообщение: {system_message}")
            return system_message
