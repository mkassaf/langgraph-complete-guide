"""
Utility-Based Robot Agent with All Four Modules

Perception → Reasoning → Action → Learning
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from warehouse_monitors.environment import (
    ActionType,
    ActionResult,
    WarehouseEnvironment,
)


# ─── Perception Module ───────────────────────────────────────────────────────

@dataclass
class Perception:
    """Structured perception for reasoning."""
    target_room: str
    distance: int
    door_locked: bool
    light_indicator: str
    obstacle_present: bool
    obstacle_type: str | None
    box_held: bool
    sensor_warning: bool = False


class PerceptionModule:
    """
    Processes raw percepts into meaningful perceptions for reasoning.
    """

    def process(self, raw_percepts: dict[str, Any]) -> Perception:
        """Convert raw sensor data to structured perception."""
        return Perception(
            target_room=raw_percepts.get("target_room", ""),
            distance=raw_percepts.get("distance", 0),
            door_locked=raw_percepts.get("door_locked", False),
            light_indicator=raw_percepts.get("light_indicator", "UNKNOWN"),
            obstacle_present=raw_percepts.get("obstacle_present", False),
            obstacle_type=raw_percepts.get("obstacle_type"),
            box_held=raw_percepts.get("box_held", False),
            sensor_warning=raw_percepts.get("sensor_warning", False),
        )


# ─── Reasoning Module ───────────────────────────────────────────────────────

@dataclass
class Decision:
    """Output of reasoning module."""
    action: ActionType
    rationale: str
    utility_scores: dict[str, float] = field(default_factory=dict)
    plan_depth: int = 0


class ReasoningModule:
    """
    Plans action sequences, evaluates utility scores, outputs decisions.
    """

    def __init__(self):
        self._options_considered: list[dict] = []
        self._decision_history: list[Decision] = []

    def decide(self, perception: Perception, learned_solutions: dict[str, str]) -> Decision:
        """
        Evaluate options, compute utility, choose best action.
        """
        options: list[tuple[ActionType, float, str]] = []

        # Obstacle handling
        if perception.obstacle_present:
            options.append((ActionType.DETOUR, 0.85, "Clear path around obstacle"))
            if perception.obstacle_type == "human":
                options.append((ActionType.WAIT, 0.6, "Wait for human to move"))

        # Door handling (before learning: human preferred; after: keypad faster)
        if perception.door_locked or perception.light_indicator == "RED":
            keypad_util = 0.9 if "locked_door" in learned_solutions else 0.4
            human_util = 0.5 if "locked_door" not in learned_solutions else 0.3
            options.append((ActionType.ENTER_KEYPAD, keypad_util, "Enter keypad code"))
            options.append((ActionType.TEXT_HUMAN, human_util, "Call human for help"))
        elif not perception.door_locked:
            options.append((ActionType.OPEN_DOOR, 0.95, "Open unlocked door"))

        # Movement
        if perception.distance > 0 and not perception.obstacle_present:
            options.append((ActionType.MOVE, 0.8, "Move toward target"))

        # Delivery
        if perception.distance == 0 and not perception.door_locked:
            options.append((ActionType.PLACE_BOX, 1.0, "Place box (goal complete)"))

        if not options:
            options = [(ActionType.WAIT, 0.5, "No clear action")]

        # Log options for monitors
        self._options_considered.append({
            "options": [(o[0].value, o[1], o[2]) for o in options],
            "perception": perception,
        })

        # Choose best by utility
        best = max(options, key=lambda x: x[1])
        action, utility, rationale = best
        utility_scores = {o[0].value: o[1] for o in options}

        decision = Decision(
            action=action,
            rationale=rationale,
            utility_scores=utility_scores,
            plan_depth=len(options),
        )
        self._decision_history.append(decision)
        return decision

    def get_options_considered(self) -> list[dict]:
        return self._options_considered

    def get_decision_history(self) -> list[Decision]:
        return self._decision_history


# ─── Action Module ───────────────────────────────────────────────────────────

@dataclass
class ActionExecution:
    """Record of action execution."""
    action: ActionType
    success: bool
    feedback: str
    side_effects: dict[str, Any]


class ActionModule:
    """
    Executes actions via effectors, manages coordination, monitors outcomes.
    """

    def __init__(self):
        self._execution_history: list[ActionExecution] = []
        self._api_call_count = 0

    def execute(
        self,
        decision: Decision,
        env: WarehouseEnvironment,
    ) -> ActionExecution:
        """Execute decision in environment."""
        action = decision.action
        kwargs: dict[str, Any] = {}
        if action == ActionType.ENTER_KEYPAD:
            room = env.get_room(env.target_room)
            kwargs["code"] = room.keypad_code if room else "1234"
            self._api_call_count += 1  # Simulate external keypad API

        result = env.apply_action(action, **kwargs)
        exec_record = ActionExecution(
            action=action,
            success=result.success,
            feedback=result.feedback,
            side_effects=result.side_effects,
        )
        self._execution_history.append(exec_record)
        return exec_record

    def get_execution_history(self) -> list[ActionExecution]:
        return self._execution_history

    def get_api_call_count(self) -> int:
        return self._api_call_count


# ─── Learning Module ─────────────────────────────────────────────────────────

@dataclass
class FeedbackEntry:
    """Single feedback event."""
    situation: str
    solution_used: str
    outcome: str
    positive: bool


class LearningModule:
    """
    Stores feedback, analyzes patterns, improves behavior over time.
    """

    def __init__(self):
        self.feedback_log: list[FeedbackEntry] = []
        self.learned_solutions: dict[str, str] = {}

    def store_feedback(self, feedback: FeedbackEntry) -> None:
        """Store feedback from environment."""
        self.feedback_log.append(feedback)

    def analyze_and_learn(self, situation: str) -> str | None:
        """
        Analyze feedback, propose improved solution.
        Returns learned solution key if improvement found.
        """
        relevant = [f for f in self.feedback_log if f.situation == situation]
        # Learn enter_keypad when text_human causes delay (waiting)
        text_human_slow = [f for f in relevant
                          if f.solution_used == "text_human" and "waiting" in f.outcome.lower()]

        if len(text_human_slow) >= 1:
            self.learned_solutions[situation] = "enter_keypad"
            return "enter_keypad"
        return None

    def get_learned_solutions(self) -> dict[str, str]:
        return self.learned_solutions


# ─── Full Agent ─────────────────────────────────────────────────────────────

class UtilityBasedRobotAgent:
    """
    Complete agent with Perception, Reasoning, Action, Learning modules.
    """

    def __init__(self, env: WarehouseEnvironment):
        self.env = env
        self.perception_module = PerceptionModule()
        self.reasoning_module = ReasoningModule()
        self.action_module = ActionModule()
        self.learning_module = LearningModule()
        self._step_count = 0
        self._current_plan: list[str] = []

    def step(self) -> dict[str, Any]:
        """
        One agent step: perceive → reason → act → learn.
        """
        self._step_count += 1

        # 1. Perception
        raw_percepts = self.env.get_percepts()
        perception = self.perception_module.process(raw_percepts)

        # 2. Reasoning
        learned = self.learning_module.get_learned_solutions()
        decision = self.reasoning_module.decide(perception, learned)

        # 3. Action
        execution = self.action_module.execute(decision, self.env)

        # 4. Learning (store feedback from action result)
        situation = "locked_door" if perception.door_locked else "obstacle"
        solution = "enter_keypad" if decision.action == ActionType.ENTER_KEYPAD else "text_human"
        self.learning_module.store_feedback(FeedbackEntry(
            situation=situation,
            solution_used=solution,
            outcome=execution.feedback,
            positive=execution.success,
        ))
        self.learning_module.analyze_and_learn(situation)

        return {
            "step": self._step_count,
            "perception": perception,
            "decision": decision,
            "execution": execution,
            "raw_percepts": raw_percepts,
        }

    def get_belief_state(self) -> dict[str, Any]:
        """Current world model for monitors."""
        return {
            "target_room": self.env.target_room,
            "task_complete": self.env.task_complete,
            "learned_solutions": self.learning_module.get_learned_solutions(),
            "step_count": self._step_count,
        }
