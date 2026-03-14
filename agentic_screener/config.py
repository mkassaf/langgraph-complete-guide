"""
Configuration for the Agentic Paper Screener.
Defines criteria, paths, and decision logic.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Paths (INPUT_PDF_DIR can be set in .env)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
_env_pdf = os.environ.get("INPUT_PDF_DIR")
if _env_pdf:
    INPUT_PDF_DIR = Path(_env_pdf)
    if not INPUT_PDF_DIR.is_absolute():
        INPUT_PDF_DIR = PROJECT_ROOT / INPUT_PDF_DIR
else:
    INPUT_PDF_DIR = PROJECT_ROOT / "output" / "pdfs"
INPUT_CSV = PROJECT_ROOT / "output" / "manual_review.csv"
OUTPUT_CSV = PROJECT_ROOT / "output" / "agentic_screening_results.csv"
OUTPUT_SUMMARIES_CSV = PROJECT_ROOT / "output" / "agentic_included_summaries.csv"

# Screening criteria definitions
# Each criterion has: id, type (inclusion/exclusion), description, expected_output (Y/N)
CRITERIA = [
    {
        "id": "I1",
        "type": "inclusion",
        "description": "LLM-based agentic systems — The paper must be about LLM-powered agents, multi-agent systems, or agentic AI.",
        "expected_for_include": "Y",
    },
    {
        "id": "I2",
        "type": "inclusion",
        "description": "Energy relevance (direct OR proxy) — The paper discusses energy consumption, power usage, carbon footprint of LLM agents, OR proxy measures: computational cost/efficiency, inference time/latency, token usage/cost reduction, memory efficiency, model compression, caching, resource optimization, throughput optimization.",
        "expected_for_include": "Y",
    },
    {
        "id": "E1",
        "type": "exclusion",
        "description": "Not LLM-based — The paper does not involve LLM-based systems.",
        "expected_for_include": "N",
    },
    {
        "id": "E2",
        "type": "exclusion",
        "description": "Not agentic — The paper does not involve agentic systems (autonomous decision-making, tool use, multi-step reasoning).",
        "expected_for_include": "N",
    },
    {
        "id": "E3",
        "type": "exclusion",
        "description": "Energy is unrelated to computational cost or resource usage — The paper discusses energy but not in relation to the LLM/agent system's own computational resources.",
        "expected_for_include": "N",
    },
    {
        "id": "E7",
        "type": "exclusion",
        "description": "Energy is discussed as an application domain — Energy is the domain the agent operates in (e.g., smart grids, renewable energy) but the paper does NOT discuss the energy consumption or efficiency of the LLM-based agent itself.",
        "expected_for_include": "N",
    },
]

# Decision logic: INCLUDE = (I1=Y AND I2=Y) AND (E1=N AND E2=N AND E3=N AND E7=N)
def compute_decision(criterion_results: dict) -> tuple[bool, str]:
    """
    Compute final INCLUDE/EXCLUDE from criterion results.
    Returns (include: bool, reason: str).
    """
    i1 = criterion_results.get("I1", "N") == "Y"
    i2 = criterion_results.get("I2", "N") == "Y"
    e1 = criterion_results.get("E1", "N") == "Y"
    e2 = criterion_results.get("E2", "N") == "Y"
    e3 = criterion_results.get("E3", "N") == "Y"
    e7 = criterion_results.get("E7", "N") == "Y"

    if not i1:
        return False, "I1: Paper is not about LLM-based agentic systems"
    if not i2:
        return False, "I2: Paper lacks energy relevance (direct or proxy)"
    if e1:
        return False, "E1: Paper is not LLM-based"
    if e2:
        return False, "E2: Paper is not agentic"
    if e3:
        return False, "E3: Energy is unrelated to computational cost/resource usage"
    if e7:
        return False, "E7: Energy is application domain only, not agent efficiency"

    return True, "All inclusion criteria met; no exclusion criteria triggered"
