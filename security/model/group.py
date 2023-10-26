class Group:

    def __init__(self, chat_id: int, group_name: str, group_info: str):
        self.chat_id = chat_id
        self.group_name = group_name
        self.group_info = group_info

    def __get_group_about(self):
        return (f"Ты являешься телеграм ботом с искусственным интеллектом. "
                f"Сейчас ты находишься в telegram группе под названием {self.group_name}. "
                f"Информация о группе: {self.group_info}. ")

    def create_system_message(self):
        system_message = {"role": "system", "content": self.__get_group_about()}
        return system_message
