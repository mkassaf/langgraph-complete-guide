"""
Interaction & Communication Monitors

Tracks agent-environment interactions and agent-human/agent-agent communication.
"""

from dataclasses import dataclass, field
from typing import Any

from warehouse_monitors.agent import (
    ActionExecution,
    ActionType,
    Decision,
    Perception,
)
from warehouse_monitors.environment import WarehouseEnvironment


@dataclass
class InteractionRecord:
    """Single interaction event."""
    action: ActionType
    response: str
    percept: dict | None = None


class InteractionMonitor:
    """
    Logs actions, observations, and environment impact.
    Concept: Full interaction timeline for audit.
    """

    def __init__(self):
        self._action_log: list[tuple[ActionType, str]] = []
        self._observation_log: list[dict] = []
        self._impact_log: list[dict] = []

    def log_action_taken(self, action: ActionType, environment_response: str) -> None:
        self._action_log.append((action, environment_response))

    def log_observation_received(self, percept: dict[str, Any]) -> None:
        self._observation_log.append(percept.copy())

    def analyze_environment_impact(self, before_state: dict, after_state: dict) -> None:
        changes = {k: (before_state.get(k), after_state.get(k))
                   for k in set(before_state) | set(after_state)
                   if before_state.get(k) != after_state.get(k)}
        if changes:
            self._impact_log.append(changes)

    def report(self) -> str:
        if not self._action_log:
            return "No interactions"
        return f"{len(self._action_log)} action(s), {len(self._observation_log)} observation(s)"


@dataclass
class MessageRecord:
    """Communication message."""
    sender: str
    receiver: str
    message: str
    response: str | None = None
    effective: bool = True


class CommunicationMonitor:
    """
    Tracks agent-to-human and agent-to-agent messages.
    Concept: Communication effectiveness evaluation.
    """

    def __init__(self):
        self._human_messages: list[MessageRecord] = []
        self._agent_messages: list[MessageRecord] = []

    def track_agent_to_human_messages(self, message: str) -> None:
        self._human_messages.append(
            MessageRecord(sender="robot", receiver="human", message=message)
        )

    def track_agent_to_agent_messages(self, sender: str, receiver: str, message: str) -> None:
        self._agent_messages.append(
            MessageRecord(sender=sender, receiver=receiver, message=message)
        )

    def evaluate_communication_effectiveness(self, message: str, response: str) -> bool:
        effective = len(response) > 0 and "success" in response.lower()
        if self._human_messages:
            self._human_messages[-1].response = response
            self._human_messages[-1].effective = effective
        return effective

    def report(self) -> str:
        total = len(self._human_messages) + len(self._agent_messages)
        if total == 0:
            return "No communications"
        effective = sum(1 for m in self._human_messages if m.effective)
        return f"{total} message(s), {effective} effective"
