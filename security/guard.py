import json
import logging
from typing import Optional

from security.model.group import Group
from security.model.user import User

logger = logging.getLogger(__name__)
USERS_FILE_PATH = "security/users.txt"
GROUPS_FILE_PATH = "security/groups.txt"


class Guard:

    def __init__(self):
        self.users = self._get_users_from_file(USERS_FILE_PATH)
        self.admins = self._get_admins()
        self.groups = self._get_groups_from_file(GROUPS_FILE_PATH)

    def _get_users_from_file(self, filename: str) -> list[User]:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        users = []
        for user_data in data:
            user = User(
                telegram_alias=user_data['telegram_alias'],
                user_name=user_data['user_name'],
                position=user_data['position'],
                gender=user_data['gender'],
                about=user_data['about']
            )
            users.append(user)
        return users

    def _get_admins(self) -> list[str]:
        admins = ["@artemnefrit"]
        return admins

    def _get_groups_from_file(self, filename: str) -> list[Group]:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        groups = []
        for group_data in data:
            group = Group(
                chat_id=int(group_data['chat_id']),
                group_name=group_data['group_name'],
                group_info=group_data['group_info']
            )
            groups.append(group)
        return groups

    def is_user_available(self, telegram_alias: str):
        telegram_alias_lower = telegram_alias.lower()
        for user in self.users:
            if user.telegram_alias == telegram_alias_lower:
                return True
        return False

    def is_user_admin(self, telegram_alias: str):
        telegram_alias_lower = telegram_alias.lower()
        for admin in self.admins:
            if admin == telegram_alias_lower:
                return True
        return False

    def is_group_available(self, group_chat_id: int):
        for group in self.groups:
            if group.chat_id == group_chat_id:
                return True
        return False

    def get_user(self, telegram_alias: str) -> Optional[User]:
        telegram_alias_lower = telegram_alias.lower()
        for user in self.users:
            if user.telegram_alias == telegram_alias_lower:
                return user
        return None

    def get_group(self, group_chat_id: int) -> Optional[Group]:
        for group in self.groups:
            if group.chat_id == group_chat_id:
                return group
        return None
