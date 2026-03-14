"""
Human Supervisor — Simulates human responder.

Receives alerts, provides information, demonstrates skills.
"""

import time
from dataclasses import dataclass


@dataclass
class HumanAlert:
    alert_id: str
    robot_id: str
    location: str
    situation_description: str
    timestamp: str


@dataclass
class HumanResponse:
    responded: bool
    arrival_time_seconds: int
    information_provided: dict
    will_demonstrate: bool


class HumanSupervisor:
    """
    Simulates a human supervisor who can:
    1. Receive alerts from robot
    2. Respond with information
    3. Physically demonstrate new skills
    """

    def receive_alert(self, alert: HumanAlert) -> HumanResponse:
        """Human decides how to respond. Simulates delay."""
        print("👤 HUMAN: Received alert. Arriving in 3 minutes...")
        time.sleep(1)
        return HumanResponse(
            responded=True,
            arrival_time_seconds=180,
            information_provided={"keypad_code": "1234"},
            will_demonstrate=True,
        )

    def provide_verbal_instruction(self) -> str:
        """Human says the code."""
        return "The door code is 1234. Let me show you."
