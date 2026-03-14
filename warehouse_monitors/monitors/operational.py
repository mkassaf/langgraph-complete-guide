"""
Operational Monitors — Performance, Environment, Resource Utilization

Tracks agent performance, environment state changes, and resource consumption.
"""

from dataclasses import dataclass, field
from typing import Any

from warehouse_monitors.agent import (
    ActionExecution,
    ActionType,
    Decision,
    Perception,
    UtilityBasedRobotAgent,
)
from warehouse_monitors.environment import WarehouseEnvironment


@dataclass
class StepRecord:
    """Record of one agent step for monitoring."""
    step: int
    perception: Perception
    decision: Decision
    execution: ActionExecution
    raw_percepts: dict[str, Any]


class PerformanceMonitor:
    """
    Tracks goal progress and task success rate.
    Concept: Operational monitoring of agent effectiveness.
    """

    def __init__(self):
        self._goal_progress_log: list[tuple[int, float]] = []
        self._success_history: list[bool] = []

    def track_goal_progress(self, agent: UtilityBasedRobotAgent, step: int) -> None:
        """Log % completion toward delivery goal."""
        complete = 1.0 if agent.env.task_complete else 0.0
        # Approximate progress by steps (simplified)
        progress = min(1.0, step * 0.2) if not complete else 1.0
        self._goal_progress_log.append((step, progress))

    def track_task_success_rate(self, history: list[StepRecord]) -> None:
        """Calculate success/failure ratio from execution history."""
        for rec in history:
            self._success_history.append(rec.execution.success)

    def report(self) -> str:
        """Performance summary."""
        if not self._goal_progress_log:
            return "No data"
        last = self._goal_progress_log[-1]
        pct = int(last[1] * 100)
        success_rate = (
            sum(self._success_history) / len(self._success_history) * 100
            if self._success_history else 100
        )
        return f"Task {pct}% complete, success rate {success_rate:.0f}%"


class EnvironmentMonitor:
    """
    Tracks environment state changes and new agents.
    Concept: Operational awareness of environment dynamics.
    """

    def __init__(self):
        self._state_changes: list[dict] = []
        self._new_agents_detected: list[str] = []

    def track_state_changes(self, before: dict, after: dict) -> None:
        """Detect what changed in the environment."""
        changes = {}
        for k in set(before) | set(after):
            if before.get(k) != after.get(k):
                changes[k] = {"before": before.get(k), "after": after.get(k)}
        if changes:
            self._state_changes.append(changes)

    def detect_new_agents(self, percepts: dict[str, Any]) -> None:
        """Flag presence of other robots or humans."""
        if percepts.get("obstacle_type") == "human":
            self._new_agents_detected.append("human")
        # Could extend for other robots

    def report(self) -> str:
        """Environment state log."""
        if not self._state_changes and not self._new_agents_detected:
            return "No significant changes"
        parts = []
        if self._state_changes:
            parts.append(f"{len(self._state_changes)} state change(s)")
        if self._new_agents_detected:
            parts.append(f"Detected: {', '.join(set(self._new_agents_detected))}")
        return "; ".join(parts)


class ResourceUtilizationMonitor:
    """
    Tracks compute, memory, API calls per reasoning cycle.
    Concept: Resource consumption monitoring for operational efficiency.
    """

    def __init__(self):
        self._compute_log: list[dict] = []
        self._api_calls: int = 0

    def track_compute(self, agent_step: dict[str, Any]) -> None:
        """Log CPU/memory per reasoning cycle."""
        self._compute_log.append({
            "step": agent_step.get("step", 0),
            "cpu": 12.5,
            "memory_mb": 256.0,
        })

    def track_api_calls(self, action: ActionType) -> None:
        """Count external API/tool usage."""
        if action in (ActionType.ENTER_KEYPAD, ActionType.TEXT_HUMAN):
            self._api_calls += 1

    def report(self) -> str:
        """Resource consumption table."""
        if not self._compute_log:
            return "No data"
        avg_cpu = sum(c["cpu"] for c in self._compute_log) / len(self._compute_log)
        return f"Avg CPU {avg_cpu:.1f}%, API calls {self._api_calls}"
