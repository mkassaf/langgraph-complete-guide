"""
Criterion Agent E2: Not agentic
Exclusion — Paper does not involve agentic systems (autonomous decision-making, tool use, etc.).
"""

import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel


CRITERION_ID = "E2"
CRITERION_DESCRIPTION = """Not agentic — The paper does not involve agentic systems. 
Agentic = autonomous decision-making, tool use, multi-step reasoning, environment interaction, 
or multi-agent collaboration. Single-call LLM without tools or iterative reasoning is NOT agentic."""


def build_prompt() -> str:
    return f"""You are a systematic review screener. Evaluate the paper against this EXCLUSION criterion:

Criterion [{CRITERION_ID}]: {CRITERION_DESCRIPTION}

Respond Y if the paper is NOT agentic (exclude). Respond N if the paper IS agentic (do not exclude for this criterion).

You MUST respond in EXACTLY this format:
Decision: Y or N
Reason: One sentence explaining why."""


def evaluate(model: BaseChatModel, paper_text: str) -> tuple[str, str]:
    """Evaluate paper against E2. Returns (decision: Y/N, reason: str)."""
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
