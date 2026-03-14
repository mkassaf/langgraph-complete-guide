"""
Agentic Paper Screener — Multi-Agent Module
Each agent is in its own file for modularity.
"""

from .reflection_agent import reflect
from .collector_agent import collect_and_decide
from .csv_generator_agent import generate_csv, get_default_columns
from .summary_agent import summarize_paper

# Criterion agents (each in own file)
from . import criterion_i1
from . import criterion_i2
from . import criterion_e1
from . import criterion_e2
from . import criterion_e3
from . import criterion_e7

CRITERION_AGENTS = {
    "I1": criterion_i1,
    "I2": criterion_i2,
    "E1": criterion_e1,
    "E2": criterion_e2,
    "E3": criterion_e3,
    "E7": criterion_e7,
}

__all__ = [
    "reflect",
    "collect_and_decide",
    "generate_csv",
    "get_default_columns",
    "summarize_paper",
    "CRITERION_AGENTS",
]
