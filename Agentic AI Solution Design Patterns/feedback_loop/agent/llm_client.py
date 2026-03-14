"""
Human Feedback Loop — LLM Client for inspection and feedback analysis.
"""

import re
from dataclasses import dataclass

from config import MAX_TOKENS, MODEL


@dataclass
class InspectionResponse:
    raw_content: str
    analysis: str
    defects_detected: list[str]
    confidence: float
    decision: str  # "approved" | "flagged"
    reasoning: str


@dataclass
class FeedbackAnalysisResponse:
    raw_content: str
    defect_updates: dict[str, dict]  # defect_id -> {confidence_delta, new_cues}
    overall_learning: str


class LLMClient:
    def __init__(self, model: str = MODEL, max_tokens: int = MAX_TOKENS):
        self.model = model
        self.max_tokens = max_tokens

    def generate(self, system_prompt: str, user_message: str) -> str:
        """Call Anthropic API and return raw text."""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic required: pip install anthropic")

        client = Anthropic()
        message = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        content = ""
        for block in message.content:
            if hasattr(block, "text"):
                content += block.text
        return content

    def parse_inspection(self, content: str) -> InspectionResponse:
        """Parse LLM inspection response."""
        analysis = ""
        m = re.search(r"ANALYSIS\s*:\s*(.+?)(?=DEFECTS_DETECTED|$)", content, re.S | re.I)
        if m:
            analysis = m.group(1).strip()[:300]

        defects = []
        m = re.search(r"DEFECTS_DETECTED\s*:\s*(.+?)(?=CONFIDENCE|$)", content, re.S | re.I)
        if m:
            raw = m.group(1).strip().lower()
            if "none" not in raw:
                for d in ["scratch", "color_fade", "micro_crack", "misalignment", "paint_bubble"]:
                    if d in raw:
                        defects.append(d)

        confidence = 0.5
        m = re.search(r"CONFIDENCE\s*:\s*([\d.]+)", content, re.I)
        if m:
            try:
                confidence = float(m.group(1))
                confidence = max(0.0, min(1.0, confidence))
            except ValueError:
                pass

        decision = "approved"
        m = re.search(r"DECISION\s*:\s*(\w+)", content, re.I)
        if m:
            d = m.group(1).strip().lower()
            if "flag" in d:
                decision = "flagged"

        reasoning = ""
        m = re.search(r"REASONING\s*:\s*(.+?)$", content, re.S | re.I)
        if m:
            reasoning = m.group(1).strip()[:200]

        return InspectionResponse(
            raw_content=content,
            analysis=analysis,
            defects_detected=defects,
            confidence=confidence,
            decision=decision,
            reasoning=reasoning,
        )

    def parse_feedback_analysis(self, content: str) -> FeedbackAnalysisResponse:
        """Parse LLM feedback analysis for defect updates."""
        defect_updates: dict[str, dict] = {}
        defect_ids = ["scratch", "color_fade", "micro_crack", "misalignment", "paint_bubble"]

        for did in defect_ids:
            pattern = rf"DEFECT\s*:\s*{did}[^D]*(?:CONFIDENCE_ADJUSTMENT|NEW_CUES)\s*:\s*([^\n]+)"
            m = re.search(pattern, content, re.I)
            if not m:
                continue
            adj = m.group(1).strip().lower()
            delta = 0.0
            if "increase" in adj:
                delta = 0.15
            elif "decrease" in adj:
                delta = -0.1

            cues = []
            cue_match = re.search(
                rf"DEFECT\s*:\s*{did}.*?NEW_CUES\s*:\s*\[?([^\]]+)\]?",
                content,
                re.S | re.I,
            )
            if cue_match:
                raw = cue_match.group(1)
                for c in raw.split(","):
                    c = c.strip().strip('"\'')
                    if c and len(c) > 2:
                        cues.append(c)

            defect_updates[did] = {"confidence_delta": delta, "new_cues": cues}

        overall = ""
        m = re.search(r"OVERALL_LEARNING\s*:\s*(.+?)$", content, re.S | re.I)
        if m:
            overall = m.group(1).strip()[:200]

        return FeedbackAnalysisResponse(
            raw_content=content,
            defect_updates=defect_updates,
            overall_learning=overall,
        )
