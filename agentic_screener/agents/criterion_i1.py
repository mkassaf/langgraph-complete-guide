"""
Criterion Agent I1: LLM-based agentic systems
Evaluates whether the paper is about LLM-powered agents, multi-agent systems, or agentic AI.
"""

import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel


CRITERION_ID = "I1"
CRITERION_DESCRIPTION = """LLM-based agentic systems — The paper must be about LLM-powered agents, 
multi-agent systems, or agentic AI. This includes systems where LLMs make autonomous decisions, 
use tools, engage in multi-step reasoning, or collaborate in multi-agent setups."""


def build_prompt() -> str:
    return f"""You are a systematic review screener. Evaluate the paper against this criterion:

Criterion [{CRITERION_ID}]: {CRITERION_DESCRIPTION}

For inclusion, the paper MUST clearly involve LLM-based agentic systems (agents, multi-agent, tool use, 
autonomous reasoning, etc.). If the paper uses LLMs only as a static model without agentic behavior, 
or uses non-LLM agents, respond N.

You MUST respond in EXACTLY this format:
Decision: Y or N
Reason: One sentence explaining why."""


def evaluate(model: BaseChatModel, paper_text: str) -> tuple[str, str]:
    """Evaluate paper against I1. Returns (decision: Y/N, reason: str)."""
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
