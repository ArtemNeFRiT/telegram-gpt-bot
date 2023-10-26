class User:

    def __init__(self, telegram_alias: str, user_name: str, position: str, gender: str, about: str):
        self.telegram_alias = telegram_alias
        self.user_name = user_name
        self.position = position
        self.gender = gender
        self.about = about

    def _get_user_about(self) -> str:
        return (f"{self.user_name}. Ник в телеграм: {self.telegram_alias}. "
                f"Пол: {self.gender}. Позиция: {self.position}. {self.about}")

    def _get_system_message(self) -> str:
        return (f"Ты являешься телеграм ботом с искусственным интеллектом. "
                f"Сейчас ты находишься в телеграм переписке. "
                f"Твой собеседоник рассказал о себе следующее: {self._get_user_about()}.")

    def create_system_message(self) -> dict:
        system_message = {"role": "system", "content": self._get_system_message()}
        return system_message
