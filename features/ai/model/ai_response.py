from features.ai.model.usage import UsageModel


class AIResponse:

    def __init__(self, assistant_message: str, usage: UsageModel):
        self.assistant_message = assistant_message
        self.usage = usage
