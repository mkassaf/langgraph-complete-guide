"""
Teaching Session — Human demonstrates skill while robot observes.

Robot sensors record every step for LLM to learn from.
"""

from dataclasses import dataclass

from environment.warehouse import Door, WarehouseEnvironment


@dataclass
class ObservationStep:
    step_number: int
    action: str
    result: str
    robot_sensor_data: dict


@dataclass
class TeachingSession:
    session_id: str
    skill_name: str
    steps_observed: list[ObservationStep]
    success: bool


class HumanTeachingSession:
    """
    Human demonstrates a skill while robot observes.
    Robot's sensors record every step.
    """

    def demonstrate_keypad_entry(
        self,
        door: Door,
        environment: WarehouseEnvironment,
    ) -> TeachingSession:
        """Human demonstrates step by step. Robot observes."""
        steps = [
            ObservationStep(1, "approach_keypad", "standing in front of keypad", {"distance_to_keypad": "0.3m"}),
            ObservationStep(2, "press_digit_1", "first digit entered", {"keypad_feedback": "beep"}),
            ObservationStep(3, "press_digit_2", "second digit entered", {"keypad_feedback": "beep"}),
            ObservationStep(4, "press_digit_3", "third digit entered", {"keypad_feedback": "beep"}),
            ObservationStep(5, "press_digit_4", "fourth digit entered", {"keypad_feedback": "beep", "light": "green"}),
            ObservationStep(6, "turn_handle", "door unlocked", {"door_status": "unlocked"}),
            ObservationStep(7, "push_door", "door opened", {"door_status": "open"}),
        ]
        environment.apply_keypad_code(door.id, door.keypad_code or "1234")
        return TeachingSession(
            session_id="ts_001",
            skill_name="use_keypad_door",
            steps_observed=steps,
            success=True,
        )
