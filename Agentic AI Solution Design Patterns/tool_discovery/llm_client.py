"""
Tool Discovery — LLM Client
"""

import re
from dataclasses import dataclass

from config import MAX_TOKENS, MODEL


@dataclass
class LLMResponse:
    raw_content: str
    thought: str | None
    action: str | None
    final: str | None
    is_complete: bool


class LLMClient:
    def __init__(self, model: str = MODEL, max_tokens: int = MAX_TOKENS):
        self.model = model
        self.max_tokens = max_tokens

    def generate(self, system_prompt: str, messages: list[dict]) -> LLMResponse:
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic required: pip install anthropic")

        client = Anthropic()
        message = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=messages,
        )
        content = ""
        for block in message.content:
            if hasattr(block, "text"):
                content += block.text

        thoughts = re.findall(r"THOUGHT\s*:\s*(.+?)(?=ACTION|FINAL|$)", content, re.DOTALL | re.IGNORECASE)
        actions = re.findall(r"ACTION\s*:\s*(.+)", content, re.IGNORECASE)
        final_m = re.search(r"FINAL\s*:\s*(.+)", content, re.DOTALL | re.IGNORECASE)

        return LLMResponse(
            raw_content=content,
            thought=thoughts[-1].strip() if thoughts else None,
            action=actions[-1].strip() if actions else None,
            final=final_m.group(1).strip() if final_m else None,
            is_complete=final_m is not None,
        )


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4
