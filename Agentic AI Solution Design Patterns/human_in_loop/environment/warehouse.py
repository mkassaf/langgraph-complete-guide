"""
Warehouse Environment — Physical warehouse simulation.

Some doors are unexpectedly locked (not in training data).
"""

from dataclasses import dataclass


@dataclass
class Room:
    id: str
    name: str
    floor: int


@dataclass
class Door:
    id: str
    room_from: str
    room_to: str
    is_locked: bool
    has_keypad: bool
    keypad_code: str | None
    is_new: bool  # True = not in agent's training data


@dataclass
class DeliveryTask:
    task_id: str
    box_id: str
    destination_room: str
    priority: str


class WarehouseEnvironment:
    """
    Simulates physical warehouse with rooms, doors, tasks.
    Some doors are unexpectedly locked (not in training data).
    """

    def __init__(self):
        self.rooms = {
            "storage": Room("storage", "Storage Area", 1),
            "room_301": Room("room_301", "Room 301", 3),
            "room_303": Room("room_303", "Room 303", 3),
            "loading": Room("loading", "Loading Bay", 1),
        }
        self.doors = {
            "door_301": Door(
                id="door_301",
                room_from="hallway",
                room_to="room_301",
                is_locked=False,
                has_keypad=False,
                keypad_code=None,
                is_new=False,
            ),
            "door_303": Door(
                id="door_303",
                room_from="hallway",
                room_to="room_303",
                is_locked=True,
                has_keypad=True,
                keypad_code="1234",
                is_new=True,
            ),
        }
        self.pending_tasks: list[DeliveryTask] = []

    def get_door_percepts(self, door_id: str) -> dict:
        """What robot sensors detect about a door."""
        door = self.doors.get(door_id)
        if not door:
            return {"error": "Unknown door"}
        status = "locked" if door.is_locked else ("open" if not door.is_locked else "closed")
        return {
            "is_blocked": door.is_locked,
            "has_keypad": door.has_keypad,
            "keypad_visible": door.has_keypad,
            "door_status": status,
            "visual_description": f"Door with keypad panel" if door.has_keypad else "Standard door with handle",
        }

    def attempt_open_door(self, door_id: str) -> dict:
        """Try to open door."""
        door = self.doors.get(door_id)
        if not door:
            return {"success": False, "reason": "Unknown door", "new_percepts": {}}
        if door.is_locked:
            return {
                "success": False,
                "reason": "Door is locked. Keypad required.",
                "new_percepts": self.get_door_percepts(door_id),
            }
        return {
            "success": True,
            "reason": "Door opened",
            "new_percepts": {"door_status": "open"},
        }

    def apply_keypad_code(self, door_id: str, code: str) -> dict:
        """Try entering a code on keypad."""
        door = self.doors.get(door_id)
        if not door or not door.has_keypad:
            return {"success": False, "reason": "No keypad on this door"}
        if code == door.keypad_code:
            door.is_locked = False
            return {"success": True, "reason": "Code accepted. Door unlocked."}
        return {"success": False, "reason": "Incorrect code"}
