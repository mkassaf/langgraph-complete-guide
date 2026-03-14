"""
Agentic Paper Screener — Multi-Agent Parallel Screening System
"""

from .run import run_screening
from .config import INPUT_CSV, OUTPUT_CSV, OUTPUT_SUMMARIES_CSV, CRITERIA, compute_decision

__all__ = [
    "run_screening",
    "INPUT_CSV",
    "OUTPUT_CSV",
    "OUTPUT_SUMMARIES_CSV",
    "CRITERIA",
    "compute_decision",
]
