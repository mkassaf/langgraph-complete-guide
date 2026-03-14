"""
Collaboration bus — expert-to-expert communication.
"""

from dataclasses import dataclass, field
from enum import Enum


class MessageType(Enum):
    INITIAL_ANALYSIS = "initial_analysis"
    CHALLENGE = "challenge"
    SUPPORT = "support"
    NEW_FINDING = "new_finding"
    CONSENSUS = "consensus"


@dataclass
class ExpertMessage:
    """
    Message exchanged between expert agents.
    Core of the iterative collaboration process.
    """

    message_id: str
    sender_expert: str
    recipient_expert: str | None  # None = broadcast to all
    message_type: MessageType
    content: str
    findings: dict = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class CollaborationRound:
    round_number: int
    messages: list[ExpertMessage]
    consensus_reached: bool
    agreed_points: list[str]
    disputed_points: list[str]


class CollaborationBus:
    """
    Manages expert-to-expert communication.
    Enables debate, challenge, and consensus building.
    """

    def __init__(self):
        self.message_log: list[ExpertMessage] = []
        self.rounds: list[CollaborationRound] = []
        self.registered_experts: dict[str, object] = {}
        self._msg_counter = 0

    def register_expert(self, expert_id: str, expert: object):
        """Register an expert agent."""
        self.registered_experts[expert_id] = expert

    def broadcast(self, message: ExpertMessage):
        """Send message to all experts."""
        self._msg_counter += 1
        message.message_id = message.message_id or f"msg_{self._msg_counter}"
        self.message_log.append(message)
        for expert_id, expert in self.registered_experts.items():
            if expert_id != message.sender_expert and hasattr(expert, "received_messages"):
                expert.received_messages.append(message)

    def send_to_expert(self, message: ExpertMessage, recipient_id: str):
        """Send message to specific expert."""
        self._msg_counter += 1
        message.message_id = message.message_id or f"msg_{self._msg_counter}"
        message.recipient_expert = recipient_id
        self.message_log.append(message)
        expert = self.registered_experts.get(recipient_id)
        if expert and hasattr(expert, "received_messages"):
            expert.received_messages.append(message)

    def get_round_summary(self, round_num: int) -> CollaborationRound | None:
        """Summarize what happened in a collaboration round."""
        for r in self.rounds:
            if r.round_number == round_num:
                return r
        return None
