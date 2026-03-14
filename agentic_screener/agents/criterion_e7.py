"""
Criterion Agent E7: Energy is discussed as an application domain
Exclusion — Energy is the domain (smart grids, etc.) but not agent efficiency.
"""

import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel


CRITERION_ID = "E7"
CRITERION_DESCRIPTION = """Energy is discussed as an application domain — The agent operates 
in an energy-related domain (smart grids, renewable energy, building energy, etc.) but the 
paper does NOT discuss the energy consumption or efficiency of the LLM-based agent itself. 
The agent optimizes energy elsewhere; we exclude unless it also addresses the agent's own compute."""


def build_prompt() -> str:
    return f"""You are a systematic review screener. Evaluate the paper against this EXCLUSION criterion:

Criterion [{CRITERION_ID}]: {CRITERION_DESCRIPTION}

Respond Y if energy is only the application domain and the paper does NOT address the agent's 
own computational efficiency (exclude). Respond N if the paper does address the agent's efficiency 
(do not exclude for this criterion).

You MUST respond in EXACTLY this format:
Decision: Y or N
Reason: One sentence explaining why."""


def evaluate(model: BaseChatModel, paper_text: str) -> tuple[str, str]:
    """Evaluate paper against E7. Returns (decision: Y/N, reason: str)."""
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
