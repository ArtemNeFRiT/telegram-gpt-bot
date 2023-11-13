import logging

from openai import OpenAI

from features.ai.model.ai_response import AIResponse
from features.ai.model.chat_data import ChatData
from features.ai.model.usage import UsageModel
from features.ai.model.user_data import UserData
from features.ai.context.context import Context
from security.guard import Guard

logger = logging.getLogger(__name__)


class OpenAIClient:
    _OPEN_AI_MODEL = "gpt-4-1106-preview"
    _OPEN_AI_DALL_E_MODEL = "dall-e-3"
    _OPEN_AI_TOKEN = ""
    _TOKENS_TO_START_OPTIMIZING = 5100  # ~1500 слов
    _TOKENS_PER_WORD = 3.4  # 1 слово = ~3.4 токена

    def __init__(self, guard: Guard):
        self.open_ai = OpenAI(
            api_key=self._OPEN_AI_TOKEN
        )
        self.context = Context(guard)

    def _generate_ai_response(self, user_messages) -> AIResponse:
        completion = self.open_ai.chat.completions.create(
            model=self._OPEN_AI_MODEL,
            messages=user_messages
        )
        assistant_message = completion.choices[0].message.content
        usage = completion.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens
        usage_model = UsageModel(prompt_tokens, completion_tokens, total_tokens)
        return AIResponse(assistant_message, usage_model)

    def clear_user_messages(self, user_name: str):
        self.context.clear_user_messages(user_name)

    def get_response_for_new_message(self, user_name: str, message: str) -> AIResponse:
        user_data = self.context.load_user_messages(user_name)
        user_messages = user_data.messages

        if not user_messages:
            system_message = self.context.create_system_message_for_private(user_name)
            if system_message is not None:
                user_messages.append(system_message)

        user_messages.append({"role": "user", "content": message})

        result = self._generate_ai_response(user_messages)

        user_messages.append({"role": "assistant", "content": result.assistant_message})

        if result.usage.total_tokens > self._TOKENS_TO_START_OPTIMIZING:
            logger.info(f"optimizing usage for user {user_name}")
            first_message = user_messages[0]
            if first_message["role"] == "system":
                user_messages.pop(1)
                user_messages.pop(2)
            else:
                user_messages.pop(0)
                user_messages.pop(1)

        user_data = UserData(user_name, user_messages, result.usage)
        self.context.save_user_messages(user_data)

        return result

    def get_response_for_new_group_message(self, chat_id: int, user_name: str, message: str) -> AIResponse:
        chat_data = self.context.load_chat_data(chat_id)
        chat_messages = chat_data.messages

        if not chat_messages:
            system_message = self.context.create_system_message_for_group(chat_id)
            if system_message is not None:
                logger.info(f"Системный промпт для чата {chat_id}: {system_message}")
                chat_messages.append(system_message)

        chat_messages.append({"role": "user", "content": message})

        result = self._generate_ai_response(chat_messages)

        chat_messages.append({"role": "assistant", "content": result.assistant_message})

        if result.usage.total_tokens > self._TOKENS_TO_START_OPTIMIZING:
            first_message = chat_messages[0]
            if first_message["role"] == "system":
                chat_messages.pop(1)
                chat_messages.pop(2)
            else:
                chat_messages.pop(0)
                chat_messages.pop(1)

        chat_data = ChatData(chat_id, chat_messages, result.usage)
        self.context.save_chat_data(chat_data)

        return result

    def generate_ai_response_with_image(self, prompt) -> str:
        response = self.open_ai.images.generate(
            model=self._OPEN_AI_DALL_E_MODEL,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url
