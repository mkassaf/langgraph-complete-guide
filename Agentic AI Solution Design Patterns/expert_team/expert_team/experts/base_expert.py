"""
Base expert class — abstract base for all expert agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ExpertAnalysis:
    expert_id: str
    domain: str
    findings: list[str]
    recommendations: list[str]
    confidence: float
    concerns: list[str]
    requires_input_from: list[str]


class BaseExpert(ABC):
    """
    Abstract base for all expert agents.
    Each has deep expertise in ONE domain.
    """

    expert_id: str = ""
    domain: str = ""
    expertise_areas: list[str] = None

    def __init__(self, llm_client, collaboration_bus):
        self.llm = llm_client
        self.bus = collaboration_bus
        self.my_analyses: list[ExpertAnalysis] = []
        self.received_messages: list = []

    @abstractmethod
    def initial_analysis(self, incident: str) -> ExpertAnalysis:
        """First independent analysis of the incident."""
        ...

    @abstractmethod
    def respond_to_peers(
        self,
        peer_messages: list,
        my_analysis: ExpertAnalysis,
    ) -> list:
        """React to other experts' findings."""
        ...

    def challenge_finding(
        self,
        peer_id: str,
        finding: str,
        reason: str,
    ):
        """Formally challenge another expert's finding."""
        from expert_team.collaboration_bus import ExpertMessage, MessageType

        return ExpertMessage(
            message_id="",
            sender_expert=self.expert_id,
            recipient_expert=peer_id,
            message_type=MessageType.CHALLENGE,
            content=f"CHALLENGE: {finding} - {reason}",
        )

    def support_finding(self, peer_id: str, finding: str):
        """Formally support another expert's finding."""
        from expert_team.collaboration_bus import ExpertMessage, MessageType

        return ExpertMessage(
            message_id="",
            sender_expert=self.expert_id,
            recipient_expert=peer_id,
            message_type=MessageType.SUPPORT,
            content=f"SUPPORT: {finding}",
        )
