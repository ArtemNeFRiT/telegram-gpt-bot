from features.ai.model.usage import UsageModel


class UserData:

    def __init__(self, user_name: str, messages, usage: UsageModel):
        self.user_name = user_name
        self.messages = messages
        self.usage = usage
