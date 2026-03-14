"""
Comms manager expert — crisis communications.
"""

import re
from expert_team.experts.base_expert import BaseExpert, ExpertAnalysis
from expert_team.collaboration_bus import ExpertMessage, MessageType
from prompts import EXPERT_ANALYSIS_PROMPT, PEER_RESPONSE_PROMPT


class CommsManagerExpert(BaseExpert):
    """
    Expert in crisis communications.
    """

    expert_id = "comms_manager"
    domain = "Crisis Communications"
    expertise_areas = [
        "stakeholder communication",
        "media response strategy",
        "customer notification messaging",
        "internal communications",
    ]

    def initial_analysis(self, incident: str) -> ExpertAnalysis:
        """LLM analyzes who to notify, message framing, media prep."""
        prompt = EXPERT_ANALYSIS_PROMPT.format(
            domain=self.domain,
            expertise_areas=", ".join(self.expertise_areas),
            incident=incident,
        )
        try:
            content = self.llm.generate(
                "You are a crisis communications expert. Be stakeholder and reputation focused.",
                prompt,
            )
            return self._parse_analysis(content)
        except Exception:
            return self._fallback_analysis()

    def _parse_analysis(self, content: str) -> ExpertAnalysis:
        findings = self._extract_list(content, "KEY_FINDINGS")
        concerns = self._extract_list(content, "IMMEDIATE_CONCERNS")
        recs = self._extract_list(content, "RECOMMENDATIONS")
        needs = self._extract_list(content, "NEEDS_INPUT_FROM")
        conf = self._extract_float(content, "CONFIDENCE", 0.70)
        return ExpertAnalysis(
            expert_id=self.expert_id,
            domain=self.domain,
            findings=findings or ["Board and customers need notification"],
            recommendations=recs or ["Prepare holding statement"],
            confidence=conf,
            concerns=concerns or ["Media inquiry risk"],
            requires_input_from=needs or ["legal_advisor"],
        )

    def _fallback_analysis(self) -> ExpertAnalysis:
        return ExpertAnalysis(
            expert_id=self.expert_id,
            domain=self.domain,
            findings=[
                "Board, customers, and regulators need notification",
                "Media inquiry likely within 24 hours",
                "Recommend proactive customer notification",
            ],
            recommendations=[
                "Prepare holding statement",
                "Designate spokesperson",
                "Coordinate with legal on messaging",
            ],
            confidence=0.70,
            concerns=["Conflicting statements", "Reputation damage", "Media scrutiny"],
            requires_input_from=["legal_advisor"],
        )

    def respond_to_peers(
        self,
        peer_messages: list[ExpertMessage],
        my_analysis: ExpertAnalysis,
    ) -> list[ExpertMessage]:
        """Coordinate messaging with legal timeline."""
        if not peer_messages:
            return []

        peer_str = "\n".join(
            f"- {m.sender_expert}: {m.content[:200]}" for m in peer_messages
        )
        my_str = f"Findings: {my_analysis.findings}\nConcerns: {my_analysis.concerns}"

        prompt = PEER_RESPONSE_PROMPT.format(
            domain=self.domain,
            my_analysis=my_str,
            peer_messages=peer_str,
        )
        try:
            content = self.llm.generate(
                "You are a comms manager. Ensure messaging aligns with legal requirements.",
                prompt,
            )
            return self._parse_peer_response(content, peer_messages)
        except Exception:
            return self._fallback_peer_response(peer_messages)

    def _parse_peer_response(
        self,
        content: str,
        peer_messages: list[ExpertMessage],
    ) -> list[ExpertMessage]:
        messages = []
        for line in content.split("\n"):
            if "CHALLENGE:" in line.upper():
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    target = parts[1].strip().split("-")[0].strip()
                    messages.append(
                        ExpertMessage(
                            "",
                            self.expert_id,
                            target,
                            MessageType.CHALLENGE,
                            line,
                        )
                    )
            elif "SUPPORT:" in line.upper():
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    target = parts[1].strip().split("-")[0].strip()
                    messages.append(
                        ExpertMessage(
                            "",
                            self.expert_id,
                            target,
                            MessageType.SUPPORT,
                            line,
                        )
                    )
        if not messages:
            messages.append(
                ExpertMessage(
                    "",
                    self.expert_id,
                    None,
                    MessageType.NEW_FINDING,
                    content[:300],
                )
            )
        return messages

    def _fallback_peer_response(
        self,
        peer_messages: list[ExpertMessage],
    ) -> list[ExpertMessage]:
        for m in peer_messages:
            if m.sender_expert == "legal_advisor" and "72" in m.content:
                return [
                    ExpertMessage(
                        "",
                        self.expert_id,
                        "legal_advisor",
                        MessageType.CHALLENGE,
                        "72 hour window is tight. Customer notification messaging needs legal review first - risk of conflicting statements.",
                    )
                ]
        return []

    def _extract_list(self, content: str, key: str) -> list[str]:
        m = re.search(rf"{key}\s*:\s*(.+?)(?=[A-Z_]+:|$)", content, re.S | re.I)
        if not m:
            return []
        raw = m.group(1).strip()
        return [x.strip() for x in raw.split("\n") if x.strip() and len(x.strip()) > 3]

    def _extract_float(self, content: str, key: str, default: float) -> float:
        m = re.search(rf"{key}\s*:\s*([\d.]+)", content, re.I)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
        return default
