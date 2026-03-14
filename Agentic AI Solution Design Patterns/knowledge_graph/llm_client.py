"""
Knowledge Graph — LLM Client

Anthropic API wrapper.
"""

from dataclasses import dataclass

from config import MAX_TOKENS, MODEL


@dataclass
class LLMResponse:
    raw_content: str
    final_answer: str | None


class LLMClient:
    def __init__(self, model: str = MODEL, max_tokens: int = MAX_TOKENS):
        self.model = model
        self.max_tokens = max_tokens

    def generate(self, system_prompt: str, user_message: str) -> LLMResponse:
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

        # Extract FINAL: block if present
        import re
        m = re.search(r"FINAL\s*:\s*(.+)", content, re.DOTALL | re.IGNORECASE)
        final_answer = m.group(1).strip() if m else content

        return LLMResponse(raw_content=content, final_answer=final_answer)
