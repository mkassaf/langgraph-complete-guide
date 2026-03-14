"""
Criterion Agent E3: Energy is unrelated to computational cost or resource usage
Exclusion — Energy discussed but not in relation to LLM/agent compute.
"""

import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel


CRITERION_ID = "E3"
CRITERION_DESCRIPTION = """Energy is unrelated to computational cost or resource usage — 
The paper discusses energy but NOT in relation to the LLM/agent system's own computational 
resources. E.g., energy for IoT devices, embedded systems, or domain-specific energy 
(not the AI system's inference cost)."""


def build_prompt() -> str:
    return f"""You are a systematic review screener. Evaluate the paper against this EXCLUSION criterion:

Criterion [{CRITERION_ID}]: {CRITERION_DESCRIPTION}

Respond Y if energy is discussed but unrelated to the LLM agent's computational cost (exclude). 
Respond N if energy relates to the agent's compute/resources (do not exclude for this criterion).

You MUST respond in EXACTLY this format:
Decision: Y or N
Reason: One sentence explaining why."""


def evaluate(model: BaseChatModel, paper_text: str) -> tuple[str, str]:
    """Evaluate paper against E3. Returns (decision: Y/N, reason: str)."""
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
