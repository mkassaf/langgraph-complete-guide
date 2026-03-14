"""
ReAct Pattern — LLM Client

Wrapper around Anthropic API. Parses ReAct format from LLM responses.
"""

import re
from dataclasses import dataclass

from config import MAX_TOKENS, MODEL


@dataclass
class LLMResponse:
    """Parsed ReAct-style LLM response."""
    raw_content: str
    thoughts: list[str]
    actions: list[str]
    final_answer: str | None
    is_complete: bool


def _extract_blocks(content: str, pattern: str) -> list[str]:
    """Extract blocks matching pattern (e.g., THOUGHT:, ACTION:, FINAL:)."""
    blocks = []
    regex = re.compile(rf"{pattern}\s*(.+?)(?={pattern}|$)", re.DOTALL | re.IGNORECASE)
    for m in regex.finditer(content):
        blocks.append(m.group(1).strip())
    # Fallback: split by pattern
    if not blocks:
        parts = re.split(rf"{pattern}", content, flags=re.IGNORECASE)
        for p in parts[1:]:
            text = p.split("OBSERVATION:")[0].split("THOUGHT:")[0].split("ACTION:")[0].strip()
            if text and len(text) > 5:
                blocks.append(text)
    return blocks


class LLMClient:
    """
    Wrapper around Anthropic API.
    Parses ReAct format from LLM responses.
    """

    def __init__(self, model: str = MODEL, max_tokens: int = MAX_TOKENS):
        self.model = model
        self.max_tokens = max_tokens

    def generate(
        self,
        system_prompt: str,
        conversation_history: list[dict],
    ) -> LLMResponse:
        """
        Call Claude API with full conversation history.
        Parse and return structured ReAct response.
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        client = Anthropic()

        message = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=conversation_history,
        )

        content = ""
        for block in message.content:
            if hasattr(block, "text"):
                content += block.text

        return self.parse_react_response(content)

    def parse_react_response(self, content: str) -> LLMResponse:
        """
        Extract THOUGHT, ACTION, FINAL blocks from raw text.
        Returns structured LLMResponse.
        """
        thoughts = _extract_blocks(content, r"THOUGHT\s*:")
        actions = _extract_blocks(content, r"ACTION\s*:")

        final_answer = None
        if re.search(r"FINAL\s*:", content, re.IGNORECASE):
            m = re.search(r"FINAL\s*:\s*(.+)", content, re.DOTALL | re.IGNORECASE)
            if m:
                final_answer = m.group(1).strip()
        is_complete = "FINAL:" in content or "FINAL :" in content

        return LLMResponse(
            raw_content=content,
            thoughts=thoughts,
            actions=actions,
            final_answer=final_answer,
            is_complete=is_complete,
        )
