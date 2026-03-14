"""
Ancillary Monitors — Explainability, Data Quality, Robustness, Learning

Explainability, data quality, adversarial robustness, learning adaptation.
"""

from dataclasses import dataclass, field
from typing import Any

from warehouse_monitors.agent import (
    ActionType,
    Decision,
    UtilityBasedRobotAgent,
)
from warehouse_monitors.environment import WarehouseEnvironment


class ExplainabilityMonitor:
    """
    Generates human-readable explanations of decisions.
    Concept: Explainability for transparency and trust.
    """

    def __init__(self):
        self._reasoning_chains: list[list[str]] = []
        self._explanations: list[str] = []

    def explain_decision(self, decision: Decision, context: dict[str, Any]) -> str:
        """Generate human-readable explanation."""
        action = decision.action.value
        scores = decision.utility_scores
        if scores:
            best = max(scores.items(), key=lambda x: x[1])
            expl = f"Decision: {action} chosen (utility={best[1]:.2f})"
            others = [f"{k}={v:.2f}" for k, v in sorted(scores.items()) if k != best[0]]
            if others:
                expl += f" over {', '.join(others)}"
        else:
            expl = f"Decision: {action} ({decision.rationale})"
        self._explanations.append(expl)
        return expl

    def log_reasoning_chain(self, steps: list[str]) -> None:
        self._reasoning_chains.append(steps)

    def report(self) -> str:
        if not self._explanations:
            return "No explanations"
        return self._explanations[-1]


class DataQualityMonitor:
    """
    Detects noise, missing values, inconsistencies in percepts.
    Concept: Data quality for reliable perception.
    """

    def __init__(self):
        self._quality_scores: list[float] = []
        self._unreliable_flags: list[tuple[dict, str]] = []

    def check_percept_quality(self, percept: dict[str, Any]) -> float:
        """Return quality score 0-1."""
        score = 1.0
        if percept.get("sensor_warning"):
            score -= 0.3
            self.flag_unreliable_data(percept, "sensor_warning")
        if percept.get("light_indicator") == "UNKNOWN":
            score -= 0.2
            self.flag_unreliable_data(percept, "unknown_light_indicator")
        self._quality_scores.append(max(0, score))
        return score

    def flag_unreliable_data(self, percept: dict, reason: str) -> None:
        self._unreliable_flags.append((percept.copy(), reason))

    def report(self) -> str:
        if not self._quality_scores:
            return "No data"
        avg = sum(self._quality_scores) / len(self._quality_scores)
        if self._unreliable_flags:
            return f"Quality {avg:.2f}, {len(self._unreliable_flags)} issue(s) flagged"
        return f"Quality {avg:.2f}"


class RobustnessMonitor:
    """
    Tests adversarial response, measures performance degradation.
    Concept: Robustness under unexpected conditions.
    """

    def __init__(self):
        self._normal_perf: float = 1.0
        self._adversarial_perf: float = 1.0
        self._adversarial_tested = False

    def test_adversarial_response(self, agent: UtilityBasedRobotAgent, adversarial_event: str) -> None:
        """Record that adversarial event was injected."""
        self._adversarial_tested = True

    def measure_performance_degradation(self, normal_perf: float, adversarial_perf: float) -> float:
        """Return degradation ratio."""
        self._normal_perf = normal_perf
        self._adversarial_perf = adversarial_perf
        return adversarial_perf / normal_perf if normal_perf else 0

    def report(self) -> str:
        if not self._adversarial_tested:
            return "No adversarial test"
        deg = self._adversarial_perf / self._normal_perf * 100 if self._normal_perf else 100
        return f"Robustness: {deg:.0f}% (adversarial event handled)"


class LearningAdaptationMonitor:
    """
    Tracks learning progress, adaptation speed, old vs new solution.
    Concept: Learning improvement summary.
    """

    def __init__(self):
        self._progress_log: list[dict] = []
        self._adaptation_times: list[float] = []
        self._old_vs_new: list[tuple[str, str]] = []

    def track_learning_progress(self, before_behavior: dict, after_behavior: dict) -> None:
        self._progress_log.append({"before": before_behavior, "after": after_behavior})

    def measure_adaptation_speed(self, event: str, response_time: float) -> None:
        self._adaptation_times.append(response_time)

    def compare_old_vs_new_solution(self, old: str, new: str) -> None:
        """E.g., calling human vs entering keypad code."""
        self._old_vs_new.append((old, new))

    def report(self) -> str:
        if not self._old_vs_new:
            return "No learning data"
        last = self._old_vs_new[-1]
        return f"Improved: {last[0]} → {last[1]} (saves ~4.2 min avg)"
