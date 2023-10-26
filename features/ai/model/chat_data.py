from features.ai.model.usage import UsageModel


class ChatData:

    def __init__(self, chat_id, messages, usage: UsageModel):
        self.chat_id = chat_id
        self.messages = messages
        self.usage = usage
