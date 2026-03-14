"""
Chain of Thought — LLM Client

Wrapper around Anthropic API. Represents the LLM component of the reasoning module.
"""

import re
from dataclasses import dataclass

from config import MAX_TOKENS, MODEL


@dataclass
class LLMResponse:
    """Response from the LLM with metadata."""
    content: str
    tokens_used: int
    reasoning_steps: list[str]  # empty if no CoT
    has_chain_of_thought: bool


def _parse_thought_steps(content: str) -> list[str]:
    """Extract THOUGHT 1, THOUGHT 2, etc. from response."""
    steps = []
    # Match "THOUGHT N - LABEL:" or "THOUGHT N:" patterns
    pattern = r"THOUGHT\s+\d+\s*(?:-\s*[A-Z]+\s*:?)?\s*\n?(.*?)(?=THOUGHT\s+\d+|$)"
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    for m in matches:
        step = m.strip()
        if step:
            steps.append(step)
    # Fallback: split by THOUGHT headers
    if not steps:
        parts = re.split(r"THOUGHT\s+\d+", content, flags=re.IGNORECASE)
        steps = [p.strip() for p in parts if p.strip() and len(p.strip()) > 20]
    return steps


class LLMClient:
    """
    Wrapper around Anthropic API.
    Represents the LLM component of the reasoning module.
    """

    def __init__(self, model: str = MODEL, max_tokens: int = MAX_TOKENS):
        self.model = model
        self.max_tokens = max_tokens

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        expect_cot: bool = False,
    ) -> LLMResponse:
        """
        Send system prompt + user message to Claude API.
        Returns response with metadata.
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

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

        # Token usage from response
        tokens_used = 0
        if hasattr(message, "usage") and message.usage:
            tokens_used = getattr(message.usage, "input_tokens", 0) + getattr(
                message.usage, "output_tokens", 0
            )

        reasoning_steps = _parse_thought_steps(content) if expect_cot else []
        has_cot = len(reasoning_steps) >= 2 or "THOUGHT" in content.upper()

        return LLMResponse(
            content=content,
            tokens_used=tokens_used,
            reasoning_steps=reasoning_steps,
            has_chain_of_thought=has_cot,
        )
