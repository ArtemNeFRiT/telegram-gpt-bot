import datetime
import json
import logging
import os

from features.ai.model.ai_response import AIResponse
from features.statistic.model.usage import Usage

STATISTIC_FILE_PATH = "statistics/statistic.txt"
logger = logging.getLogger(__name__)
STATISTIC_FOLDER_NAME = "statistics"


class StatisticProvider:

    def save_statistic(self, user_name: str, ai_response: AIResponse):
        self._create_statistic_folder()

        statistics_file_full_path = self._get_statistic_file_full_path()

        try:
            with open(statistics_file_full_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []

        user_found = False
        for entry in data:
            if entry['user'] == user_name:
                entry['calls'] += 1
                entry['prompt_tokens'] = entry.get('prompt_tokens', 0) + ai_response.usage.prompt_tokens
                entry['completion_tokens'] = entry.get('completion_tokens', 0) + ai_response.usage.completion_tokens
                entry['total_tokens'] = entry.get('total_tokens', 0) + ai_response.usage.total_tokens
                user_found = True
                break

        if not user_found:
            data.append({
                'user': user_name,
                'calls': 1,
                'prompt_tokens': ai_response.usage.prompt_tokens,
                'completion_tokens': ai_response.usage.completion_tokens,
                'total_tokens': ai_response.usage.total_tokens
            })

        with open(statistics_file_full_path, 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def _get_statistic_file_full_path(self) -> str:
        now = datetime.datetime.now()
        statistics_file_name = f"{now.month}.{now.year}.txt"

        return STATISTIC_FOLDER_NAME + "/" + statistics_file_name

    def _create_statistic_folder(self):
        if not os.path.exists(STATISTIC_FOLDER_NAME):
            os.makedirs(STATISTIC_FOLDER_NAME)

    def find_users_with_max_usage(self, count: int) -> list[Usage]:
        statistics_file_full_path = self._get_statistic_file_full_path()
        try:
            with open(statistics_file_full_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            logger.error("Файл не найден")
            return []

        usages = [Usage(user['user'], user['calls'], user['prompt_tokens'], user['completion_tokens'],
                        user['total_tokens']) for user in data]
        sorted_usages = sorted(usages, key=lambda x: x.completion_words_count, reverse=True)

        return sorted_usages[:count]
