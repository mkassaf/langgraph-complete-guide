"""
Chain of Thought — Comparator

Runs both modes and produces side-by-side comparison.
Demonstrates why CoT matters for complex tasks.
"""

import re
from dataclasses import dataclass

from agent import ControllerResult


@dataclass
class Analysis:
    """Analysis of a single response."""
    assumptions_count: int
    missing_considerations: list[str]
    vague_interpretations: list[str]
    reasoning_steps_count: int
    specificity_score: int  # 1-10


@dataclass
class ComparisonReport:
    """Full comparison of standard vs CoT modes."""
    without_cot: ControllerResult
    with_cot: ControllerResult
    without_cot_analysis: Analysis
    with_cot_analysis: Analysis


def _score_specificity(text: str) -> int:
    """Score 1-10 based on specificity of recommendations."""
    score = 5
    if any(word in text.lower() for word in ["specific", "concrete", "example", "e.g."]):
        score += 2
    if any(word in text.lower() for word in ["budget", "cost", "price"]):
        score += 1
    if any(word in text.lower() for word in ["date", "time", "schedule"]):
        score += 1
    if "?" in text or "clarify" in text.lower():
        score += 1  # Asking for clarification is good
    if len(text) < 200:
        score -= 2
    if "assum" in text.lower() and text.lower().count("assum") > 2:
        score -= 2
    return max(1, min(10, score))


def _find_missing_considerations(text: str) -> list[str]:
    """Check for missing considerations."""
    missing = []
    checks = [
        ("budget", "Budget"),
        ("availability", "Team availability"),
        ("catering", "Catering details"),
        ("venue", "Venue selection"),
        ("activities", "Activity specifics"),
    ]
    for key, label in checks:
        if key not in text.lower():
            missing.append(label)
    return missing


def _find_vague_interpretations(text: str) -> list[str]:
    """Find vague terms that weren't clarified."""
    vague = []
    if "engaging" in text.lower() and "define" not in text.lower() and "clarify" not in text.lower():
        vague.append("'Engaging' - not defined")
    if "half-day" in text.lower() and "hour" not in text.lower() and "am" not in text.lower():
        vague.append("'Half-day' - duration not specified")
    return vague


class ChainOfThoughtComparator:
    """
    Runs both modes and produces side-by-side comparison.
    Demonstrates why CoT matters for complex tasks.
    """

    def __init__(self, agent):
        self.agent = agent

    def run_comparison(self, request: str) -> ComparisonReport:
        """
        1. Run agent WITHOUT Chain of Thought
        2. Run agent WITH Chain of Thought
        3. Analyze differences
        4. Generate comparison report
        """
        without_cot = self.agent.plan_without_cot(request)
        with_cot = self.agent.plan_with_cot(request)

        without_cot_analysis = self.analyze_response(without_cot)
        with_cot_analysis = self.analyze_response(with_cot)

        return ComparisonReport(
            without_cot=without_cot,
            with_cot=with_cot,
            without_cot_analysis=without_cot_analysis,
            with_cot_analysis=with_cot_analysis,
        )

    def analyze_response(self, result: ControllerResult) -> Analysis:
        """
        Check for:
        - Assumptions made without validation
        - Missing considerations (availability, budget, etc.)
        - Vague interpretations ("engaging" = ?)
        - Number of reasoning steps
        - Specificity of recommendations
        """
        content = result.llm_response.content
        reasoning_steps = result.llm_response.reasoning_steps
        if not reasoning_steps and "THOUGHT" in content.upper():
            # Parse if not already parsed
            pattern = r"THOUGHT\s+\d+"
            reasoning_steps = re.split(pattern, content, flags=re.IGNORECASE)
            reasoning_steps = [s.strip() for s in reasoning_steps if len(s.strip()) > 30]

        return Analysis(
            assumptions_count=len(result.assumptions_made),
            missing_considerations=_find_missing_considerations(content),
            vague_interpretations=_find_vague_interpretations(content),
            reasoning_steps_count=len(reasoning_steps),
            specificity_score=_score_specificity(content),
        )
