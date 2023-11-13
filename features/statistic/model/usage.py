class Usage:

    def __init__(self, user_name: str, calls: int, prompt_tokens: int, completion_tokens: int, total_tokens: int):
        self.user_name = user_name
        self.calls = calls
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
