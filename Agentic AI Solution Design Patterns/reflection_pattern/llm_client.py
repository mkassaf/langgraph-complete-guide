"""
Reflection Pattern — LLM Client

Anthropic API wrapper with reflection-specific parsing.
"""

import re
from dataclasses import dataclass

from config import MAX_TOKENS, MODEL


@dataclass
class LLMResponse:
    raw_content: str
    has_improvement: bool
    has_correction: bool
    has_pattern_switch: bool
    improvement_text: str | None
    correction_action: str | None
    pattern_switch_to: str | None  # "react" | "cot" | None
    verdict: str | None


def _extract_block(content: str, pattern: str) -> str | None:
    m = re.search(rf"{pattern}\s*(.+?)(?=CHANGES MADE|VERDICT|VERIFIED|CORRECTION NEEDED|REASON|SWITCH TO|KEEP:|$)", content, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else None


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
        return self.parse_reflection_response(content)

    def parse_reflection_response(self, content: str) -> LLMResponse:
        improvement_text = _extract_block(content, r"IMPROVED OUTPUT\s*:")
        has_improvement = bool(improvement_text)

        m = re.search(r"CORRECTION NEEDED\s*:\s*(\w+\([^)]+\))", content, re.IGNORECASE)
        correction_action = m.group(1).strip() if m else None
        has_correction = bool(correction_action)

        pattern_switch_to = None
        if re.search(r"SWITCH TO REACT", content, re.IGNORECASE):
            pattern_switch_to = "react"
        elif re.search(r"SWITCH TO COT", content, re.IGNORECASE):
            pattern_switch_to = "cot"
        has_pattern_switch = pattern_switch_to is not None

        verdict = None
        if "OUTPUT IS SATISFACTORY" in content.upper():
            verdict = "SATISFACTORY"
        elif "VERIFIED" in content.upper():
            verdict = "VERIFIED"
        elif "KEEP:" in content.upper():
            verdict = "KEEP"

        return LLMResponse(
            raw_content=content,
            has_improvement=has_improvement,
            has_correction=has_correction,
            has_pattern_switch=has_pattern_switch,
            improvement_text=improvement_text,
            correction_action=correction_action,
            pattern_switch_to=pattern_switch_to,
            verdict=verdict,
        )
