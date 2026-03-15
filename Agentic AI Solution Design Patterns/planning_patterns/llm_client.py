"""LLM client for planning patterns."""

from config import MAX_TOKENS, MODEL


class LLMClient:
    def __init__(self, model: str = MODEL, max_tokens: int = MAX_TOKENS):
        self.model = model
        self.max_tokens = max_tokens
        self._call_count = 0

    def generate(self, system_prompt: str, user_message: str) -> str:
        self._call_count += 1
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic required: pip install anthropic")

        client = Anthropic()
        message = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return "".join(b.text for b in message.content if hasattr(b, "text"))

    def get_call_count(self) -> int:
        return self._call_count

    def reset_call_count(self):
        self._call_count = 0
