import datetime
import json
import logging
import os

from features.statistic.model.usage import Usage

STATISTIC_FILE_PATH = "statistics/statistic.txt"
logger = logging.getLogger(__name__)
STATISTIC_FOLDER_NAME = "statistics"


class StatisticProvider:

    def _save_statistic(self, user_name: str, words_count: int):
        file = open(STATISTIC_FILE_PATH, "a+")
        file.seek(0)

        previous_key = None
        previous_number = 0

        for line in file:
            stored_key, stored_number = line.strip().split(":")
            if stored_key == user_name:
                previous_key = stored_key
                previous_number = int(stored_number)
                break

        new_number = words_count + previous_number

        file.seek(0)
        lines = file.readlines()

        if previous_key:
            updated_line = f"{previous_key}:{new_number}\n"
            lines[lines.index(f"{previous_key}:{previous_number}\n")] = updated_line
        else:
            updated_line = f"{user_name}:{new_number}\n"
            lines.append(updated_line)

        file.seek(0)
        file.truncate()
        file.writelines(lines)

        file.close()

    def save_statistic(self, user_name: str, completion_words_count: int):
        self._create_statistic_folder()
        self._save_statistic(user_name, completion_words_count)

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
                entry['completion_words_count'] += completion_words_count
                user_found = True
                break

        if not user_found:
            data.append({
                'user': user_name,
                'calls': 1,
                'completion_words_count': completion_words_count
            })

        with open(statistics_file_full_path, 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        logger.info(f"Данные пользователя {user_name} обновлены.")

    def _get_statistic_file_full_path(self) -> str:
        now = datetime.datetime.now()
        statistics_file_name = f"{now.month}.{now.year}.txt"

        return STATISTIC_FOLDER_NAME + "/" + statistics_file_name

    def _create_statistic_folder(self):
        if not os.path.exists(STATISTIC_FOLDER_NAME):
            os.makedirs(STATISTIC_FOLDER_NAME)

    def find_users_with_max_usage(self, count: int):
        statistics_file_full_path = self._get_statistic_file_full_path()
        try:
            with open(statistics_file_full_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            logger.error("Файл не найден")
            return []

        usages = [Usage(user['user'], user['calls'], user['completion_words_count']) for user in data]
        sorted_usages = sorted(usages, key=lambda x: x.completion_words_count, reverse=True)

        return sorted_usages[:count]
