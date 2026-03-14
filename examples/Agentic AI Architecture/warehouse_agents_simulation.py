"""
Smart Warehouse Agent Simulation

Demonstrates all four AI agent types operating in a warehouse environment:
- Simple Reflex Agent: condition-action rules only
- Model-Based Reflex Agent: internal model + rules
- Goal-Based Agent: plan to reach goal, learns over time
- Utility-Based Agent: maximize utility, learns over time

Each agent has four modules (Learning only for Goal-Based and Utility-Based):
- PerceptionModule: collect/interpret environment data
- ReasoningModule: decide what action to take
- ActionModule: execute via effectors
- LearningModule: store feedback, improve (Goal-Based, Utility-Based only)

Scenario: Room 303 has locked door + human obstacle.
Run: python examples/warehouse_agents_simulation.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ─── Environment State (dataclasses) ──────────────────────────────────────────

@dataclass
class RoomState:
    """State of a single room in the warehouse."""
    room_id: str
    distance: int  # meters from current position
    door_locked: bool
    obstacle_present: bool  # e.g., human blocking


@dataclass
class EnvironmentState:
    """Full environment state."""
    current_position: str
    target_room: str
    rooms: dict[str, RoomState]
    box_held: bool = False
    task_complete: bool = False


class ActionType(Enum):
    """Actions the agent can take."""
    STOP = "stop"
    WAIT = "wait"
    MOVE = "move"
    DETOUR = "detour"
    TEXT_MANAGER = "text_manager"
    ENTER_KEYPAD = "enter_keypad"
    OPEN_DOOR = "open_door"
    PLACE_BOX = "place_box"


# ─── Environment ─────────────────────────────────────────────────────────────

class Environment:
    """
    Warehouse environment. Provides percepts, applies actions, returns feedback.
    """

    def __init__(self, target_room: str = "303"):
        self.target_room = target_room
        # Scenario: room 303 has locked door + human obstacle; room 301 is clear
        self.rooms = {
            "301": RoomState("301", distance=10, door_locked=False, obstacle_present=False),
            "302": RoomState("302", distance=20, door_locked=False, obstacle_present=True),
            "303": RoomState("303", distance=30, door_locked=True, obstacle_present=True),
        }
        self.robot_position = "warehouse"
        self.box_held = True
        self.task_complete = False

    def get_percepts(self) -> dict[str, Any]:
        """
        Raw percepts from environment (what sensors would report).
        """
        target = self.rooms.get(self.target_room)
        if not target:
            return {"error": "Unknown room"}
        return {
            "distance": target.distance,
            "door_locked": target.door_locked,
            "obstacle_present": target.obstacle_present,
            "target_room": self.target_room,
            "current_position": self.robot_position,
        }

    def apply_action(self, action: ActionType, **kwargs) -> dict[str, Any]:
        """
        Apply action to environment. Returns outcome.
        """
        if action == ActionType.STOP:
            return {"success": True, "message": "Agent stopped"}
        if action == ActionType.WAIT:
            return {"success": True, "message": "Agent waiting"}
        if action == ActionType.DETOUR:
            return {"success": True, "message": "Detoured around obstacle"}
        if action == ActionType.TEXT_MANAGER:
            return {"success": True, "message": "Manager notified; waiting for door unlock"}
        if action == ActionType.ENTER_KEYPAD:
            return {"success": True, "message": "Entered code; door unlocked"}
        if action == ActionType.OPEN_DOOR:
            if self.rooms[self.target_room].door_locked:
                return {"success": False, "message": "Door locked"}
            return {"success": True, "message": "Door opened"}
        if action == ActionType.PLACE_BOX:
            self.task_complete = True
            return {"success": True, "message": "Box delivered"}
        if action == ActionType.MOVE:
            return {"success": True, "message": "Moved toward target"}
        return {"success": False, "message": "Unknown action"}

    def get_feedback(self) -> dict[str, Any]:
        """
        Feedback from environment (monitors, supervisor, etc.).
        """
        return {
            "task_complete": self.task_complete,
            "position": self.robot_position,
        }


# ─── Module Base Classes ─────────────────────────────────────────────────────

class PerceptionModule(ABC):
    """Base: transforms raw percepts into perceptions for reasoning."""

    @abstractmethod
    def perceive(self, raw_percepts: dict, agent_state: dict) -> dict:
        """Process raw percepts into perceptions."""
        pass


class ReasoningModule(ABC):
    """Base: decides what action(s) to take."""

    @abstractmethod
    def reason(self, perceptions: dict, agent_state: dict) -> tuple[ActionType, str]:
        """Return (action, reason)."""
        pass


class ActionModule(ABC):
    """Base: executes actions via effectors."""

    @abstractmethod
    def execute(self, action: ActionType, **kwargs) -> dict:
        """Execute action, return outcome."""
        pass


class LearningModule(ABC):
    """Base: stores feedback, improves agent over time."""

    @abstractmethod
    def learn(self, perceptions: dict, action: ActionType, outcome: dict, feedback: dict) -> dict:
        """Process experience; return what was learned."""
        pass


# ─── Simple Reflex Agent ─────────────────────────────────────────────────────

class SimpleReflexPerception(PerceptionModule):
    """
    Simple Reflex: Collect raw percepts only. No interpretation.
    (Lesson: percepts = raw sensor data, no feature extraction)
    """
    def perceive(self, raw_percepts: dict, agent_state: dict) -> dict:
        # Concept: Raw percepts only — door status, obstacle present
        return {
            "door_locked": raw_percepts.get("door_locked", False),
            "obstacle_present": raw_percepts.get("obstacle_present", False),
        }


class SimpleReflexReasoning(ReasoningModule):
    """
    Simple Reflex: Lookup predefined rules only. No planning, no model.
    (Lesson: condition-action rules, direct mapping)
    """
    def reason(self, perceptions: dict, agent_state: dict) -> tuple[ActionType, str]:
        # Concept: Predefined rules — if obstacle → stop; if door locked → stop
        if perceptions.get("obstacle_present"):
            return ActionType.STOP, "Predefined rule: obstacle present → stop"
        if perceptions.get("door_locked"):
            return ActionType.STOP, "Predefined rule: door locked → stop"
        return ActionType.MOVE, "Predefined rule: no obstacle, door open → move"


class SimpleReflexAction(ActionModule):
    """Simple Reflex: Execute single action from rule."""
    def __init__(self, env: Environment):
        self.env = env

    def execute(self, action: ActionType, **kwargs) -> dict:
        return self.env.apply_action(action, **kwargs)


# ─── Model-Based Reflex Agent ────────────────────────────────────────────────

class ModelBasedReflexPerception(PerceptionModule):
    """
    Model-Based: Form perceptions + update internal environment model.
    (Lesson: maintains internal state/model of world)
    """
    def __init__(self):
        self.internal_model: dict = {}

    def perceive(self, raw_percepts: dict, agent_state: dict) -> dict:
        # Concept: Update internal model — enables reasoning about unobserved state
        self.internal_model["door_locked"] = raw_percepts.get("door_locked", False)
        self.internal_model["obstacle_present"] = raw_percepts.get("obstacle_present", False)
        self.internal_model["distance"] = raw_percepts.get("distance", 0)
        return dict(self.internal_model)


class ModelBasedReflexReasoning(ReasoningModule):
    """
    Model-Based: Use internal model + predefined rules.
    """
    def reason(self, perceptions: dict, agent_state: dict) -> tuple[ActionType, str]:
        if perceptions.get("obstacle_present"):
            return ActionType.DETOUR, "Model: obstacle → detour (use alternate path)"
        if perceptions.get("door_locked"):
            return ActionType.TEXT_MANAGER, "Model: door locked → text manager"
        return ActionType.MOVE, "Model: clear path → move"


class ModelBasedReflexAction(ActionModule):
    """Model-Based: Simple actions informed by model logic."""
    def __init__(self, env: Environment):
        self.env = env

    def execute(self, action: ActionType, **kwargs) -> dict:
        return self.env.apply_action(action, **kwargs)


# ─── Goal-Based Agent ────────────────────────────────────────────────────────

class GoalBasedPerception(PerceptionModule):
    """
    Goal-Based: Compare current state to goal state.
    (Lesson: perceptions include goal gap — what blocks achievement)
    """
    def perceive(self, raw_percepts: dict, agent_state: dict) -> dict:
        goal = agent_state.get("goal", "deliver box to room")
        target = raw_percepts.get("target_room", "?")
        return {
            "current_state": {
                "position": raw_percepts.get("current_position"),
                "target": target,
                "door_locked": raw_percepts.get("door_locked"),
                "obstacle_present": raw_percepts.get("obstacle_present"),
            },
            "goal_state": {"box_delivered_to": target},
            "gap": self._compute_gap(raw_percepts),
        }

    def _compute_gap(self, percepts: dict) -> list[str]:
        """What's blocking goal achievement?"""
        gap = []
        if percepts.get("obstacle_present"):
            gap.append("obstacle")
        if percepts.get("door_locked"):
            gap.append("door_locked")
        return gap


class GoalBasedReasoning(ReasoningModule):
    """
    Goal-Based: Plan multi-step action sequences to reach goal.
    (Lesson: planning — sequence of actions to close goal gap)
    """
    def reason(self, perceptions: dict, agent_state: dict) -> tuple[ActionType, str]:
        gap = perceptions.get("gap", [])
        if not gap:
            return ActionType.PLACE_BOX, "Plan: no obstacles → place box"
        # Plan: resolve obstacles first
        if "obstacle" in gap:
            return ActionType.DETOUR, "Plan step 1: detour around obstacle"
        if "door_locked" in gap:
            return ActionType.TEXT_MANAGER, "Plan step 2: door locked → text manager"
        return ActionType.MOVE, "Plan: move toward goal"


class GoalBasedAction(ActionModule):
    """Goal-Based: Execute action sequences, manage effectors, monitor progress."""
    def __init__(self, env: Environment):
        self.env = env
        self.sequence: list[ActionType] = []

    def execute(self, action: ActionType, **kwargs) -> dict:
        self.sequence.append(action)
        return self.env.apply_action(action, **kwargs)


class GoalBasedLearning(LearningModule):
    """
    Goal-Based: Improve planning efficiency over time.
    """
    def __init__(self):
        self.experience: list[dict] = []

    def learn(self, perceptions: dict, action: ActionType, outcome: dict, feedback: dict) -> dict:
        self.experience.append({
            "gap": perceptions.get("gap", []),
            "action": action.value,
            "outcome": outcome,
            "feedback": feedback,
        })
        # Learned: if door locked often, prefer keypad over text manager
        door_locked_count = sum(1 for e in self.experience if "door_locked" in e.get("gap", []))
        if door_locked_count >= 2:
            return {"learned": "Prefer ENTER_KEYPAD over TEXT_MANAGER for repeated door locks"}
        return {"learned": "No refinement yet"}


# ─── Utility-Based Agent ─────────────────────────────────────────────────────

class UtilityBasedPerception(PerceptionModule):
    """
    Utility-Based: Evaluate environment against potential utility scores.
    """
    def perceive(self, raw_percepts: dict, agent_state: dict) -> dict:
        return {
            "door_locked": raw_percepts.get("door_locked", False),
            "obstacle_present": raw_percepts.get("obstacle_present", False),
            "distance": raw_percepts.get("distance", 0),
            "target_room": raw_percepts.get("target_room", ""),
        }


class UtilityBasedReasoning(ReasoningModule):
    """
    Utility-Based: Explore multiple options, calculate utility, pick best.
    (Lesson: utility function — score each option, maximize expected outcome)
    """
    def reason(self, perceptions: dict, agent_state: dict) -> tuple[ActionType, str]:
        obstacle = perceptions.get("obstacle_present", False)
        locked = perceptions.get("door_locked", False)

        # Build options with utility scores based on situation
        options = []
        if obstacle:
            options.extend([(ActionType.STOP, 0), (ActionType.DETOUR, 70)])
        if locked:
            options.extend([(ActionType.TEXT_MANAGER, 30), (ActionType.ENTER_KEYPAD, 90)])
        if not obstacle and not locked:
            options = [(ActionType.MOVE, 50), (ActionType.PLACE_BOX, 100)]
        if not options:
            options = [(ActionType.STOP, 0), (ActionType.DETOUR, 70),
                       (ActionType.TEXT_MANAGER, 30), (ActionType.ENTER_KEYPAD, 90)]

        best = max(options, key=lambda x: x[1])
        return best[0], f"Utility: {[(a.value, u) for a, u in options]} → best={best[0].value} (score={best[1]})"


class UtilityBasedAction(ActionModule):
    """Utility-Based: Coordinate complex action sequences with full oversight."""
    def __init__(self, env: Environment):
        self.env = env

    def execute(self, action: ActionType, **kwargs) -> dict:
        return self.env.apply_action(action, **kwargs)


class UtilityBasedLearning(LearningModule):
    """
    Utility-Based: Improve utility scores and make outcomes more effective.
    """
    def __init__(self):
        self.outcomes: list[dict] = []
        self.utility_adjustments: dict = {}

    def learn(self, perceptions: dict, action: ActionType, outcome: dict, feedback: dict) -> dict:
        self.outcomes.append({
            "action": action.value,
            "outcome": outcome,
            "feedback": feedback,
        })
        # Adjust: if TEXT_MANAGER led to slow feedback, lower its utility
        if action == ActionType.TEXT_MANAGER and feedback.get("feedback_negative"):
            self.utility_adjustments["TEXT_MANAGER"] = -10
            return {"learned": "Lower TEXT_MANAGER utility; prefer ENTER_KEYPAD"}
        return {"learned": "Utility scores unchanged"}


# ─── Agent Classes ───────────────────────────────────────────────────────────

class Agent(ABC):
    """Base agent with four modules."""

    def __init__(self, env: Environment, name: str):
        self.env = env
        self.name = name
        self.perception: PerceptionModule = None
        self.reasoning: ReasoningModule = None
        self.action: ActionModule = None
        self.learning: LearningModule | None = None
        self.state: dict = {}

    def run_step(self) -> dict:
        """Execute one step: perceive → reason → act → (learn)."""
        raw = self.env.get_percepts()
        perceptions = self.perception.perceive(raw, self.state)
        action, reason = self.reasoning.reason(perceptions, self.state)
        outcome = self.action.execute(action)
        feedback = self.env.get_feedback()

        learned = {}
        if self.learning:
            learned = self.learning.learn(perceptions, action, outcome, feedback)

        return {
            "perceptions": perceptions,
            "reasoning": reason,
            "action": action,
            "outcome": outcome,
            "learned": learned,
        }


class SimpleReflexAgent(Agent):
    """Simple Reflex: condition-action rules only."""
    def __init__(self, env: Environment):
        super().__init__(env, "SimpleReflexAgent")
        self.perception = SimpleReflexPerception()
        self.reasoning = SimpleReflexReasoning()
        self.action = SimpleReflexAction(env)
        self.learning = None


class ModelBasedReflexAgent(Agent):
    """Model-Based: internal model + rules."""
    def __init__(self, env: Environment):
        super().__init__(env, "ModelBasedReflexAgent")
        self.perception = ModelBasedReflexPerception()
        self.reasoning = ModelBasedReflexReasoning()
        self.action = ModelBasedReflexAction(env)
        self.learning = None


class GoalBasedAgent(Agent):
    """Goal-Based: plan to reach goal, learn over time."""
    def __init__(self, env: Environment):
        super().__init__(env, "GoalBasedAgent")
        self.state["goal"] = "deliver box to room"
        self.perception = GoalBasedPerception()
        self.reasoning = GoalBasedReasoning()
        self.action = GoalBasedAction(env)
        self.learning = GoalBasedLearning()


class UtilityBasedAgent(Agent):
    """Utility-Based: maximize utility, learn over time."""
    def __init__(self, env: Environment):
        super().__init__(env, "UtilityBasedAgent")
        self.perception = UtilityBasedPerception()
        self.reasoning = UtilityBasedReasoning()
        self.action = UtilityBasedAction(env)
        self.learning = UtilityBasedLearning()


# ─── Simulation ──────────────────────────────────────────────────────────────

def reset_environment(env: Environment):
    """Reset env to initial state for fair comparison."""
    env.task_complete = False
    env.robot_position = "warehouse"
    env.box_held = True


def run_simulation():
    """Run all four agents on the same delivery task."""
    env = Environment(target_room="303")

    agents = [
        SimpleReflexAgent(env),
        ModelBasedReflexAgent(env),
        GoalBasedAgent(env),
        UtilityBasedAgent(env),
    ]

    results = []

    for agent in agents:
        reset_environment(env)
        print("\n" + "=" * 65)
        print(f"[{agent.name.upper()}]")
        print("=" * 65)

        step = agent.run_step()

        print(f"  Perception: {step['perceptions']}")
        print(f"  Reasoning:  {step['reasoning']}")
        print(f"  Action:     {step['action'].value}")
        if agent.learning and step["learned"]:
            print(f"  Learning:   {step['learned']}")
        else:
            print(f"  Learning:   N/A")
        print(f"  Result:    {step['outcome']}")

        results.append({
            "agent": agent.name,
            "action": step["action"].value,
            "outcome": step["outcome"],
            "learned": step.get("learned", {}),
        })

    # Comparison summary
    print("\n" + "=" * 65)
    print("COMPARISON SUMMARY")
    print("=" * 65)
    print("Scenario: Room 303 — locked door + human obstacle")
    print()
    for r in results:
        learned_str = str(r["learned"]) if r["learned"] else "N/A"
        print(f"  {r['agent']:25} → {r['action']:15} | {r['outcome']['message']}")
        if r["learned"]:
            print(f"  {'':25}   Learning: {learned_str}")
    print("=" * 65)


if __name__ == "__main__":
    run_simulation()
