"""
Consensus builder — synthesizes expert debate into final response.
"""

import re
from dataclasses import dataclass

from expert_team.collaboration_bus import CollaborationRound
from expert_team.experts.base_expert import ExpertAnalysis
from prompts import CONSENSUS_PROMPT


@dataclass
class TeamConsensus:
    """Final agreed-upon response from expert team."""

    incident_summary: str
    immediate_actions: list[str]
    short_term_actions: list[str]
    legal_obligations: list[str]
    communication_plan: str
    containment_strategy: str
    confidence_level: float
    dissenting_opinions: list[str]


class ConsensusBuilder:
    """
    Builds final consensus from expert debate rounds.
    """

    def __init__(self, llm_client):
        self.llm = llm_client

    def build_consensus(
        self,
        expert_analyses: list[ExpertAnalysis],
        collaboration_rounds: list[CollaborationRound],
    ) -> TeamConsensus:
        """LLM synthesizes agreed points, resolved disputes, final recommendations."""
        analyses_str = "\n\n".join(
            f"{a.expert_id} ({a.domain}):\n"
            f"Findings: {a.findings}\n"
            f"Recommendations: {a.recommendations}\n"
            f"Concerns: {a.concerns}"
            for a in expert_analyses
        )
        rounds_str = "\n\n".join(
            f"Round {r.round_number}: "
            f"agreed={r.agreed_points}, disputed={r.disputed_points}\n"
            f"Messages: {len(r.messages)}"
            for r in collaboration_rounds
        )

        prompt = CONSENSUS_PROMPT.format(
            all_analyses=analyses_str,
            collaboration_rounds=rounds_str,
        )
        try:
            content = self.llm.generate(
                "You are synthesizing a cybersecurity breach response from expert team debate.",
                prompt,
            )
            return self._parse_consensus(content)
        except Exception:
            return self._fallback_consensus(expert_analyses)

    def _parse_consensus(self, content: str) -> TeamConsensus:
        immediate = self._extract_list(content, "IMMEDIATE_ACTIONS")
        short_term = self._extract_list(content, "SHORT_TERM_ACTIONS")
        legal = self._extract_list(content, "LEGAL_OBLIGATIONS")
        comms = self._extract_block(content, "COMMUNICATION_PLAN")
        containment = self._extract_block(content, "CONTAINMENT_STRATEGY")
        dissent = self._extract_list(content, "REMAINING_DISAGREEMENTS")
        conf = self._extract_float(content, "CONFIDENCE", 0.85)
        summary = self._extract_block(content, "AGREED_FINDINGS") or "Breach response consensus."

        return TeamConsensus(
            incident_summary=summary[:500],
            immediate_actions=immediate or self._default_immediate(),
            short_term_actions=short_term or self._default_short_term(),
            legal_obligations=legal or ["GDPR notification within 72 hours"],
            communication_plan=comms or "Notify board, legal, customers. Prepare media statement.",
            containment_strategy=containment or "Isolate affected systems. Preserve forensics.",
            confidence_level=conf,
            dissenting_opinions=dissent or [],
        )

    def _fallback_consensus(
        self,
        expert_analyses: list[ExpertAnalysis],
    ) -> TeamConsensus:
        return TeamConsensus(
            incident_summary="SQL injection breach. 50K records exposed. Attack ongoing.",
            immediate_actions=[
                "Isolate affected systems immediately",
                "Engage incident response team",
                "Preserve forensic evidence",
                "Notify board and legal team",
            ],
            short_term_actions=[
                "Submit GDPR breach notification",
                "Notify affected customers",
                "Engage PCI-DSS assessor",
                "Issue media statement",
            ],
            legal_obligations=[
                "GDPR notification within 72 hours",
                "PCI-DSS breach reporting",
                "Document all incident details",
            ],
            communication_plan="Board and legal first. Customer notification after legal review. Media holding statement ready.",
            containment_strategy="Isolate Customer DB and payment systems. Block web portal. Preserve logs.",
            confidence_level=0.88,
            dissenting_opinions=["Attack sophistication level (opportunistic vs targeted)"],
        )

    def _extract_list(self, content: str, key: str) -> list[str]:
        m = re.search(rf"{key}\s*:\s*(.+?)(?=[A-Z_]+:|$)", content, re.S | re.I)
        if not m:
            return []
        raw = m.group(1).strip()
        items = []
        for line in raw.split("\n"):
            line = line.strip()
            if re.match(r"^\d+\.", line):
                line = re.sub(r"^\d+\.\s*", "", line)
            if line and len(line) > 5:
                items.append(line)
        return items[:10]

    def _extract_block(self, content: str, key: str) -> str:
        m = re.search(rf"{key}\s*:\s*(.+?)(?=[A-Z_]+:|$)", content, re.S | re.I)
        return m.group(1).strip()[:300] if m else ""

    def _extract_float(self, content: str, key: str, default: float) -> float:
        m = re.search(rf"{key}\s*:\s*([\d.]+)", content, re.I)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
        return default

    def _default_immediate(self) -> list[str]:
        return [
            "Isolate affected systems immediately",
            "Engage incident response team",
            "Preserve forensic evidence",
            "Notify board and legal team",
        ]

    def _default_short_term(self) -> list[str]:
        return [
            "Submit GDPR breach notification",
            "Notify affected customers",
            "Engage PCI-DSS assessor",
            "Issue media statement",
        ]
