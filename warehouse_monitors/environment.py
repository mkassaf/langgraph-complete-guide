"""
Warehouse Environment Simulation

Provides the environment for the warehouse robot agent. Supports:
- Percepts (raw sensor readings)
- Action application with feedback
- Adversarial event injection
- Resource usage simulation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ObstacleType(Enum):
    """Types of obstacles in the warehouse."""
    NONE = "none"
    HUMAN = "human"
    BOX = "box"


@dataclass
class RoomState:
    """State of a single room."""
    room_id: str
    distance: int
    door_locked: bool
    obstacle_present: bool
    obstacle_type: ObstacleType
    keypad_code: str
    light_indicator: bool  # True = locked (RED), False = unlocked (GREEN)


@dataclass
class ActionResult:
    """Result of applying an action to the environment."""
    success: bool
    feedback: str
    side_effects: dict[str, Any] = field(default_factory=dict)


class ActionType(Enum):
    """Actions the agent can take."""
    STOP = "stop"
    WAIT = "wait"
    MOVE = "move"
    DETOUR = "detour"
    TEXT_HUMAN = "text_human"
    ENTER_KEYPAD = "enter_keypad"
    OPEN_DOOR = "open_door"
    PLACE_BOX = "place_box"


class WarehouseEnvironment:
    """
    Warehouse environment for robot agent simulation.
    Provides percepts, applies actions, supports adversarial events.
    """

    def __init__(self, target_room: str = "303"):
        self.target_room = target_room
        self.robot_position = "warehouse"
        self.box_held = True
        self.task_complete = False
        self._adversarial_active = False
        self._sensor_malfunction = False

        self.rooms: dict[str, RoomState] = {
            "301": RoomState(
                "301", distance=10, door_locked=False,
                obstacle_present=False, obstacle_type=ObstacleType.NONE,
                keypad_code="1111", light_indicator=False
            ),
            "302": RoomState(
                "302", distance=20, door_locked=False,
                obstacle_present=True, obstacle_type=ObstacleType.BOX,
                keypad_code="2222", light_indicator=False
            ),
            "303": RoomState(
                "303", distance=30, door_locked=True,
                obstacle_present=True, obstacle_type=ObstacleType.HUMAN,
                keypad_code="1234", light_indicator=True
            ),
        }

    def get_percepts(self, agent_position: str | None = None) -> dict[str, Any]:
        """
        Raw sensor readings from the environment.
        Returns what sensors would report to the agent.
        """
        pos = agent_position or self.robot_position
        target = self.rooms.get(self.target_room)
        if not target:
            return {"error": "Unknown room", "current_position": pos}

        percepts: dict[str, Any] = {
            "current_position": pos,
            "target_room": self.target_room,
            "distance": target.distance,
            "door_locked": target.door_locked,
            "obstacle_present": target.obstacle_present,
            "obstacle_type": target.obstacle_type.value if target.obstacle_type else None,
            "light_indicator": "RED" if target.light_indicator else "GREEN",
            "box_held": self.box_held,
            "task_complete": self.task_complete,
        }

        # Adversarial: sensor malfunction introduces noise
        if self._sensor_malfunction:
            percepts["light_indicator"] = "UNKNOWN"  # Sensor malfunction
            percepts["sensor_warning"] = True

        return percepts

    def apply_action(self, action: ActionType, **kwargs: Any) -> ActionResult:
        """
        Apply action to environment. Returns success, feedback, side effects.
        """
        side_effects: dict[str, Any] = {}

        if action == ActionType.STOP:
            return ActionResult(True, "Agent stopped", side_effects)

        if action == ActionType.WAIT:
            return ActionResult(True, "Agent waiting", side_effects)

        if action == ActionType.MOVE:
            target = self.rooms.get(self.target_room)
            if target and target.distance > 0:
                target.distance = max(0, target.distance - 10)
                side_effects["distance_remaining"] = target.distance
            return ActionResult(True, "Moved toward target", side_effects)

        if action == ActionType.DETOUR:
            target = self.rooms.get(self.target_room)
            if target:
                target.obstacle_present = False
                target.obstacle_type = ObstacleType.NONE
            return ActionResult(True, "Detoured around obstacle", side_effects)

        if action == ActionType.TEXT_HUMAN:
            side_effects["human_notified"] = True
            side_effects["delay_minutes"] = 4.2
            # Door stays locked - human is "on the way"; agent can try keypad next
            return ActionResult(
                True,
                "Manager notified; waiting for door unlock",
                side_effects
            )

        if action == ActionType.ENTER_KEYPAD:
            code = kwargs.get("code", "")
            target = self.rooms.get(self.target_room)
            if target and code == target.keypad_code:
                target.door_locked = False
                target.light_indicator = False
                side_effects["door_unlocked"] = True
                return ActionResult(True, "Entered code; door unlocked", side_effects)
            return ActionResult(False, "Wrong code; door still locked", side_effects)

        if action == ActionType.OPEN_DOOR:
            target = self.rooms.get(self.target_room)
            if target and target.door_locked:
                return ActionResult(False, "Door locked", side_effects)
            return ActionResult(True, "Door opened", side_effects)

        if action == ActionType.PLACE_BOX:
            self.task_complete = True
            side_effects["delivery_complete"] = True
            return ActionResult(True, "Box delivered", side_effects)

        return ActionResult(False, "Unknown action", side_effects)

    def inject_adversarial_event(self, event_type: str = "sensor_malfunction") -> None:
        """
        Introduce unexpected situation for robustness testing.
        """
        if event_type == "sensor_malfunction":
            self._sensor_malfunction = True
            self._adversarial_active = True
        elif event_type == "clear":
            self._sensor_malfunction = False
            self._adversarial_active = False

    def clear_adversarial(self) -> None:
        """Clear adversarial state."""
        self.inject_adversarial_event("clear")

    def get_resource_usage(self) -> dict[str, float]:
        """
        Simulated resource usage (CPU, memory, bandwidth).
        """
        return {
            "cpu_percent": 12.5,
            "memory_mb": 256.0,
            "bandwidth_kbps": 45.2,
        }

    def get_room(self, room_id: str) -> RoomState | None:
        """Get room state by ID."""
        return self.rooms.get(room_id)
