"""
Message router — routes messages between hierarchy layers.
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class MessageDirection(Enum):
    DOWN = "down"  # Orchestrator → Sub-orchestrator → Worker
    UP = "up"  # Worker → Sub-orchestrator → Orchestrator
    LATERAL = "lateral"  # Between same-level agents


@dataclass
class HierarchyMessage:
    """
    Message that flows through the hierarchy.
    """

    message_id: str
    sender_id: str
    sender_layer: int
    recipient_id: str
    recipient_layer: int
    direction: MessageDirection
    content: dict
    task_context: str


class MessageRouter:
    """
    Routes messages between all layers.
    Task delegation always goes layer by layer.
    """

    def __init__(self):
        self.agents: dict[str, tuple[object, int]] = {}  # id -> (agent, layer)
        self.message_log: list[HierarchyMessage] = []
        self._msg_counter = 0

    def register_agent(self, agent_id: str, agent: object, layer: int):
        """Register agent with its layer number."""
        self.agents[agent_id] = (agent, layer)

    def route(self, message: HierarchyMessage) -> HierarchyMessage:
        """Route message to recipient, log it."""
        self._msg_counter += 1
        message.message_id = message.message_id or f"msg_{self._msg_counter}"
        self.message_log.append(message)
        recipient = self.agents.get(message.recipient_id)
        if recipient:
            agent, _ = recipient
            if hasattr(agent, "receive_message"):
                agent.receive_message(message)
        return message

    def send(self, sender_id: str, sender_layer: int, recipient_id: str, recipient_layer: int, direction: MessageDirection, content: dict, task_context: str = "") -> HierarchyMessage:
        """Convenience method to create and route a message."""
        msg = HierarchyMessage(
            message_id="",
            sender_id=sender_id,
            sender_layer=sender_layer,
            recipient_id=recipient_id,
            recipient_layer=recipient_layer,
            direction=direction,
            content=content,
            task_context=task_context,
        )
        return self.route(msg)

    def get_messages_by_layer(self, layer: int) -> list[HierarchyMessage]:
        """Get all messages that passed through a layer."""
        return [m for m in self.message_log if m.sender_layer == layer or m.recipient_layer == layer]
