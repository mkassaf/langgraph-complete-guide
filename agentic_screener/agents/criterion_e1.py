"""
Criterion Agent E1: Not LLM-based
Exclusion — Paper does not involve LLM-based systems.
"""

import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel


CRITERION_ID = "E1"
CRITERION_DESCRIPTION = """Not LLM-based — The paper does not involve LLM-based systems. 
The core system uses traditional ML, RL without LLMs, or other non-LLM approaches. 
LLM used only for data generation or as a minor component does not count as LLM-based."""


def build_prompt() -> str:
    return f"""You are a systematic review screener. Evaluate the paper against this EXCLUSION criterion:

Criterion [{CRITERION_ID}]: {CRITERION_DESCRIPTION}

Respond Y if the paper is NOT primarily LLM-based (exclude). Respond N if the paper IS LLM-based (do not exclude for this criterion).

You MUST respond in EXACTLY this format:
Decision: Y or N
Reason: One sentence explaining why."""


def evaluate(model: BaseChatModel, paper_text: str) -> tuple[str, str]:
    """Evaluate paper against E1. Returns (decision: Y/N, reason: str)."""
    prompt = build_prompt()
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=paper_text),
    ]
    result = model.invoke(messages)
    return _parse_result(result.content)


def _parse_result(text: str) -> tuple[str, str]:
    decision = "N"
    reason = ""
    if match := re.search(r"Decision:\s*(Y|N)", text, re.IGNORECASE):
        decision = match.group(1).upper()
    if match := re.search(r"Reason:\s*(.+)", text, re.IGNORECASE | re.DOTALL):
        reason = match.group(1).strip().split("\n")[0]
    return decision, reason
