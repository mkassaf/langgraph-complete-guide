"""
Human-in-the-Loop — LLM Client
"""

import re
from dataclasses import dataclass

from config import MAX_TOKENS, MODEL


@dataclass
class LLMResponse:
    raw_content: str
    assessment: str | None
    can_proceed: bool
    needs_human: bool
    help_type: str | None
    skill_name: str | None
    skill_steps: list[str]
    action_sequence: list[str]


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

        m_cp = re.search(r"CAN_PROCEED\s*:\s*(\w+)", content, re.I)
        can_proceed = m_cp and "yes" in (m_cp.group(1) or "").lower()
        m_nh = re.search(r"NEEDS_HUMAN\s*:\s*(\w+)", content, re.I)
        needs_human = m_nh and "yes" in (m_nh.group(1) or "").lower()
        help_type = None
        m = re.search(r"HELP_TYPE\s*:\s*(\w+)", content, re.I)
        if m:
            help_type = m.group(1).strip()
        skill_name = None
        m = re.search(r"SKILL_NAME\s*:\s*(.+)", content, re.I)
        if m:
            skill_name = m.group(1).strip()
        skill_steps = re.findall(r"\d+\.\s*(.+)", content)
        action_seq = re.findall(r"ACTION\s*:\s*(\S+\([^)]*\))", content, re.I)

        return LLMResponse(
            raw_content=content,
            assessment=None,
            can_proceed=can_proceed,
            needs_human=needs_human,
            help_type=help_type,
            skill_name=skill_name,
            skill_steps=skill_steps[:10],
            action_sequence=action_seq,
        )
