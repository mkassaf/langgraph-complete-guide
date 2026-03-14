"""
Criterion Agent I2: Energy relevance (direct OR proxy)
Evaluates whether the paper discusses energy consumption or proxy measures (cost, latency, tokens, etc.).
"""

import re
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel


CRITERION_ID = "I2"
CRITERION_DESCRIPTION = """Energy relevance (direct OR proxy) — The paper discusses:
- DIRECT: energy consumption, power usage, carbon footprint of LLM agents
- PROXY: computational cost/efficiency, inference time/latency, token usage/cost reduction, 
  memory efficiency, model compression, caching, resource optimization, throughput optimization

Proxy measures are anything that reduces the computational work of the LLM agent (fewer tokens, 
caching, compression, efficient memory, batching, etc.)."""


def build_prompt() -> str:
    return f"""You are a systematic review screener. Evaluate the paper against this criterion:

Criterion [{CRITERION_ID}]: {CRITERION_DESCRIPTION}

For inclusion (Y), the paper must discuss the energy/computational efficiency of the LLM-based 
agentic system ITSELF — not energy as an application domain (e.g., smart grids, renewable energy).

You MUST respond in EXACTLY this format:
Decision: Y or N
Reason: One sentence explaining why."""


def evaluate(model: BaseChatModel, paper_text: str) -> tuple[str, str]:
    """Evaluate paper against I2. Returns (decision: Y/N, reason: str)."""
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
