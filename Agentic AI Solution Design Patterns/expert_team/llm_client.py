"""
LLM client for Specialized Expert Team.
"""

from config import MAX_TOKENS, MODEL


class LLMClient:
    def __init__(self, model: str = MODEL, max_tokens: int = MAX_TOKENS):
        self.model = model
        self.max_tokens = max_tokens

    def generate(self, system_prompt: str, user_message: str) -> str:
        """Call Anthropic API and return raw text."""
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
        content = ""
        for block in message.content:
            if hasattr(block, "text"):
                content += block.text
        return content
