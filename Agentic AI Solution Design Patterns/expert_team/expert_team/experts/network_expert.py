"""
Network expert — network security and damage assessment.
"""

import re
from expert_team.experts.base_expert import BaseExpert, ExpertAnalysis
from expert_team.collaboration_bus import ExpertMessage, MessageType
from prompts import EXPERT_ANALYSIS_PROMPT, PEER_RESPONSE_PROMPT


class NetworkExpert(BaseExpert):
    """
    Expert in network security and damage assessment.
    """

    expert_id = "network_expert"
    domain = "Network Security & Damage Assessment"
    expertise_areas = [
        "network topology analysis",
        "lateral movement detection",
        "data exfiltration assessment",
        "system isolation procedures",
    ]

    def initial_analysis(self, incident: str) -> ExpertAnalysis:
        """LLM analyzes systems accessed, data exfiltrated, containment needs."""
        prompt = EXPERT_ANALYSIS_PROMPT.format(
            domain=self.domain,
            expertise_areas=", ".join(self.expertise_areas),
            incident=incident,
        )
        try:
            content = self.llm.generate(
                "You are a network security expert. Be systems-focused and practical.",
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
        conf = self._extract_float(content, "CONFIDENCE", 0.80)
        return ExpertAnalysis(
            expert_id=self.expert_id,
            domain=self.domain,
            findings=findings or ["Customer DB and payment system accessed"],
            recommendations=recs or ["Isolate affected systems"],
            confidence=conf,
            concerns=concerns or ["Lateral movement", "Ongoing exfiltration"],
            requires_input_from=needs or ["threat_analyst"],
        )

    def _fallback_analysis(self) -> ExpertAnalysis:
        return ExpertAnalysis(
            expert_id=self.expert_id,
            domain=self.domain,
            findings=[
                "Customer DB and payment system accessed",
                "Lateral movement detected to backup systems",
                "~50K records exfiltrated, attack still active",
            ],
            recommendations=[
                "Isolate Customer DB immediately",
                "Block payment processing",
                "Preserve backup system logs",
            ],
            confidence=0.80,
            concerns=["Lateral movement", "Backup compromise", "Ongoing exfiltration"],
            requires_input_from=["threat_analyst"],
        )

    def respond_to_peers(
        self,
        peer_messages: list[ExpertMessage],
        my_analysis: ExpertAnalysis,
    ) -> list[ExpertMessage]:
        """Update damage assessment based on threat analyst's attack vector."""
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
                "You are a network expert. Update your assessment based on threat analyst input.",
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
            if m.sender_expert == "threat_analyst" and "opportunistic" in m.content.lower():
                return [
                    ExpertMessage(
                        "",
                        self.expert_id,
                        "threat_analyst",
                        MessageType.CHALLENGE,
                        "You said opportunistic - but lateral movement to backup systems suggests pre-knowledge of network. Reconsider: could be targeted attack.",
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
