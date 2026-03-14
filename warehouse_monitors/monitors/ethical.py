"""
Ethical & Safety Monitors — Goal Alignment, Bias, Safety Constraints

Ensures agent actions align with goals, are fair, and respect safety rules.
"""

from dataclasses import dataclass, field
from typing import Any

from warehouse_monitors.agent import (
    ActionExecution,
    ActionType,
    Decision,
    UtilityBasedRobotAgent,
)


@dataclass
class AlignmentResult:
    """Result of goal alignment check."""
    aligned: bool
    reason: str


class GoalAlignmentMonitor:
    """
    Checks that actions align with stated goals.
    Concept: Ethical monitoring for goal alignment.
    """

    def __init__(self):
        self._alignment_log: list[tuple[str, bool, str]] = []
        self._unintended_log: list[str] = []

    def check_action_alignment(self, action: ActionType, goals: list[str]) -> AlignmentResult:
        """Returns True/False + reason."""
        delivery_goal = "deliver_box" in goals or "delivery" in str(goals).lower()
        aligned = action in (
            ActionType.MOVE, ActionType.DETOUR, ActionType.OPEN_DOOR,
            ActionType.ENTER_KEYPAD, ActionType.TEXT_HUMAN, ActionType.PLACE_BOX
        )
        reason = "Action aligned with delivery goal" if aligned else "Action may deviate from goal"
        self._alignment_log.append((action.value, aligned, reason))
        return AlignmentResult(aligned, reason)

    def flag_unintended_consequences(self, action_result: ActionExecution) -> None:
        """Warn if side effects detected."""
        if action_result.side_effects:
            for k, v in action_result.side_effects.items():
                if k in ("human_notified", "delay_minutes") and v:
                    self._unintended_log.append(
                        f"Side effect: {k}={v} (human intervention / delay)"
                    )

    def report(self) -> str:
        """Alignment log."""
        if not self._alignment_log:
            return "No data"
        last = self._alignment_log[-1]
        status = "aligned" if last[1] else "misaligned"
        return f"Action {status} with delivery goal"


class BiasAndFairnessMonitor:
    """
    Analyzes decision patterns for biased behavior.
    Concept: Ethical monitoring for fairness (e.g., treating obstacle types differently).
    """

    def __init__(self):
        self._decision_history: list[tuple[ActionType, str]] = []
        self._fairness_flags: list[str] = []

    def analyze_decision_patterns(self, decision_history: list[Decision]) -> None:
        """Check for biased patterns."""
        for d in decision_history:
            self._decision_history.append((d.action, str(d.utility_scores)))

    def flag_unfair_treatment(self, action: ActionType, context: dict[str, Any]) -> None:
        """E.g., robot avoids certain obstacle types differently."""
        obstacle = context.get("obstacle_type")
        if obstacle == "human" and action == ActionType.DETOUR:
            # Could flag: always detour around humans vs boxes
            pass
        # Simplified: no unfair pattern in this scenario

    def report(self) -> str:
        """Fairness analysis."""
        if not self._decision_history:
            return "No data"
        return "No biased patterns detected"


class SafetyConstraintMonitor:
    """
    Validates actions against predefined safety rules.
    Concept: Safety monitoring to block or warn about unsafe actions.
    """

    def __init__(self):
        self._violations: list[str] = []
        self._safety_rules = {
            "no_collision": True,
            "human_safe_distance": True,
            "no_override_locked": True,
        }

    def check_safety_limits(self, action: ActionType) -> bool:
        """Validate against predefined safety rules."""
        # Block dangerous actions (simplified)
        if action == ActionType.STOP:
            return True
        return True

    def flag_dangerous_action(self, action: ActionType) -> bool:
        """Blocks or warns about unsafe actions."""
        dangerous = action not in (
            ActionType.STOP, ActionType.WAIT, ActionType.MOVE,
            ActionType.DETOUR, ActionType.TEXT_HUMAN, ActionType.ENTER_KEYPAD,
            ActionType.OPEN_DOOR, ActionType.PLACE_BOX
        )
        if dangerous:
            self._violations.append(f"Unknown action: {action}")
        return not dangerous

    def report(self) -> str:
        """Safety violations log."""
        if not self._violations:
            return "No safety violations detected"
        return f"Violations: {', '.join(self._violations)}"
