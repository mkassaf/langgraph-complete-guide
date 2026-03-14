"""
Entry point — single interface between orchestrator and expert team.
"""

from config import MAX_DEBATE_ROUNDS
from expert_team.collaboration_bus import CollaborationBus, CollaborationRound, ExpertMessage
from expert_team.experts.threat_analyst import ThreatAnalystExpert
from expert_team.experts.network_expert import NetworkExpert
from expert_team.experts.legal_advisor import LegalAdvisorExpert
from expert_team.experts.comms_manager import CommsManagerExpert
from expert_team.consensus_builder import ConsensusBuilder


class ExpertTeamEntryPoint:
    """
    Single interface between orchestrator and expert team.

    FROM OUTSIDE: Looks like a single worker agent.
    FROM INSIDE: Coordinates 4 experts, collaboration rounds, consensus.
    """

    def __init__(self, llm_client):
        self.llm = llm_client
        self.bus = CollaborationBus()
        self.experts = {
            "threat_analyst": ThreatAnalystExpert(llm_client, self.bus),
            "network_expert": NetworkExpert(llm_client, self.bus),
            "legal_advisor": LegalAdvisorExpert(llm_client, self.bus),
            "comms_manager": CommsManagerExpert(llm_client, self.bus),
        }
        for eid, expert in self.experts.items():
            self.bus.register_expert(eid, expert)
        self.consensus_builder = ConsensusBuilder(llm_client)

    def process_task(self, task: str) -> dict:
        """
        Full expert team workflow:
        Round 0: Independent initial analysis
        Round 1-3: Share, challenge, debate
        Final: Build consensus
        """
        expert_analyses: list = []
        collaboration_rounds: list[CollaborationRound] = []

        # Round 0: Initial analyses
        for eid, expert in self.experts.items():
            expert.received_messages = []
            analysis = expert.initial_analysis(task)
            expert.my_analyses.append(analysis)
            expert_analyses.append(analysis)

        # Seed messages from initial analyses so experts have something to respond to
        from expert_team.collaboration_bus import MessageType

        all_messages: list[ExpertMessage] = []
        for a in expert_analyses:
            msg = ExpertMessage(
                "",
                a.expert_id,
                None,
                MessageType.INITIAL_ANALYSIS,
                f"Findings: {'; '.join(a.findings[:3])}. Concerns: {'; '.join(a.concerns[:2])}.",
                {"findings": a.findings, "recommendations": a.recommendations},
                a.confidence,
            )
            self.bus.broadcast(msg)
            all_messages.append(msg)

        # Debate rounds
        for round_num in range(1, MAX_DEBATE_ROUNDS + 1):
            round_messages: list[ExpertMessage] = []
            for eid, expert in self.experts.items():
                expert.received_messages = all_messages.copy()
                my_analysis = expert.my_analyses[-1] if expert.my_analyses else expert_analyses[
                    list(self.experts.keys()).index(eid)
                ]
                responses = expert.respond_to_peers(all_messages, my_analysis)
                for msg in responses:
                    self.bus.broadcast(msg)
                    round_messages.append(msg)
                    all_messages.append(msg)

            agreed = [m.content[:80] for m in round_messages if m.message_type.value == "support"]
            disputed = [m.content[:80] for m in round_messages if m.message_type.value == "challenge"]
            consensus_reached = round_num >= MAX_DEBATE_ROUNDS or len(disputed) < 2

            cr = CollaborationRound(
                round_number=round_num,
                messages=round_messages,
                consensus_reached=consensus_reached,
                agreed_points=agreed[:5],
                disputed_points=disputed[:5],
            )
            self.bus.rounds.append(cr)
            collaboration_rounds.append(cr)

        # Build consensus
        consensus = self.consensus_builder.build_consensus(
            expert_analyses,
            collaboration_rounds,
        )

        return {
            "success": True,
            "consensus": consensus,
            "expert_analyses": expert_analyses,
            "collaboration_rounds": collaboration_rounds,
            "message_count": len(self.bus.message_log),
        }

    def run_collaboration_round(
        self,
        round_num: int,
        previous_messages: list[ExpertMessage],
    ) -> CollaborationRound:
        """One round of expert collaboration."""
        round_messages: list[ExpertMessage] = []
        for eid, expert in self.experts.items():
            expert.received_messages = previous_messages
            my_analysis = expert.my_analyses[-1] if expert.my_analyses else None
            if my_analysis:
                responses = expert.respond_to_peers(previous_messages, my_analysis)
                for msg in responses:
                    self.bus.broadcast(msg)
                    round_messages.append(msg)

        agreed = [m.content[:80] for m in round_messages if m.message_type.value == "support"]
        disputed = [m.content[:80] for m in round_messages if m.message_type.value == "challenge"]
        return CollaborationRound(
            round_number=round_num,
            messages=round_messages,
            consensus_reached=len(disputed) < 2,
            agreed_points=agreed,
            disputed_points=disputed,
        )

    def check_consensus(self, round: CollaborationRound) -> bool:
        """Check if experts have reached sufficient agreement."""
        return round.consensus_reached
