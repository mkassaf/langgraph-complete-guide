"""
State & Belief Monitors — Internal State, Planning, Belief Accuracy

Tracks agent's world model, intention changes, and belief vs reality.
"""

from dataclasses import dataclass, field
from typing import Any

from warehouse_monitors.agent import (
    Decision,
    UtilityBasedRobotAgent,
)
from warehouse_monitors.environment import WarehouseEnvironment


@dataclass
class BeliefSnapshot:
    """Agent's current world model."""
    beliefs: dict[str, Any]
    step: int


class InternalStateMonitor:
    """
    Captures agent's current world model and intention changes.
    Concept: Internal state tracking for transparency.
    """

    def __init__(self):
        self._belief_history: list[BeliefSnapshot] = []
        self._intention_changes: list[tuple[dict, dict]] = []

    def snapshot_beliefs(self, agent: UtilityBasedRobotAgent) -> None:
        """Capture agent's current world model."""
        beliefs = agent.get_belief_state()
        step = agent._step_count
        self._belief_history.append(BeliefSnapshot(beliefs=beliefs, step=step))

    def track_intention_changes(self, before: dict, after: dict) -> None:
        """Log when plans/goals shift."""
        if before != after:
            self._intention_changes.append((before, after))

    def report(self) -> str:
        if not self._belief_history:
            return "No belief data"
        return f"{len(self._belief_history)} belief snapshot(s)"


class PlanningAndDecisionMonitor:
    """
    Logs options considered, decisions made, planning depth.
    Concept: Decision audit trail for explainability.
    """

    def __init__(self):
        self._options_log: list[list] = []
        self._decisions_log: list[tuple[Any, str]] = []
        self._plan_depth_log: list[int] = []

    def log_options_considered(self, options_list: list) -> None:
        self._options_log.append(options_list)

    def log_decision_made(self, chosen_option: Any, rationale: str) -> None:
        self._decisions_log.append((chosen_option, rationale))

    def track_planning_depth(self, plan: Any) -> None:
        depth = len(plan) if hasattr(plan, "__len__") else 1
        self._plan_depth_log.append(depth)

    def report(self) -> str:
        if not self._decisions_log:
            return "No decisions"
        return f"{len(self._decisions_log)} decision(s), avg depth {sum(self._plan_depth_log) / len(self._plan_depth_log):.1f}" if self._plan_depth_log else "No planning data"


class BeliefAccuracyMonitor:
    """
    Compares agent belief to actual state.
    Concept: Flag incorrect beliefs (e.g., thought door unlocked but it wasn't).
    """

    def __init__(self):
        self._accuracy_log: list[tuple[bool, str]] = []
        self._incorrect_flags: list[str] = []

    def compare_belief_to_reality(self, belief: dict, actual_state: dict) -> bool:
        """Return True if belief matches reality."""
        # Simplified: check key fields
        match = True
        for k in ("task_complete", "target_room"):
            if k in belief and k in actual_state:
                if belief[k] != actual_state[k]:
                    match = False
                    self.flag_incorrect_belief(belief, actual_state)
        self._accuracy_log.append((match, "matches" if match else "mismatch"))
        return match

    def flag_incorrect_belief(self, belief: dict, actual: dict) -> None:
        """E.g., agent thought door was unlocked but it wasn't."""
        diff = {k: (belief.get(k), actual.get(k))
                for k in set(belief) | set(actual)
                if belief.get(k) != actual.get(k)}
        self._incorrect_flags.append(str(diff))

    def report(self) -> str:
        if not self._accuracy_log:
            return "No data"
        matches = sum(1 for m, _ in self._accuracy_log if m)
        total = len(self._accuracy_log)
        pct = matches / total * 100 if total else 100
        return f"Belief accuracy {pct:.0f}%"
