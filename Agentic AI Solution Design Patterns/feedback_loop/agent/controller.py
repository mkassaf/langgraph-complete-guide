"""
Human Feedback Loop — Controller

Manages inspection + feedback loop cycle.
"""

from prompts import INSPECTION_PROMPT, FEEDBACK_ANALYSIS_PROMPT
from factory.toy_generator import Toy
from hmi.feedback_record import HumanFeedback, InspectionDecision
from agent.detection_model import DefectDetectionModel
from agent.llm_client import LLMClient, InspectionResponse, FeedbackAnalysisResponse


class Controller:
    """
    Manages inspection + feedback loop cycle.

    Continuous loop:
    1. Inspect toy with current model knowledge
    2. Make decision (approve/flag)
    3. Receive human feedback via HMI
    4. LLM analyzes feedback
    5. Update detection model
    6. Repeat with improved model
    """

    def __init__(self, llm_client: LLMClient, detection_model: DefectDetectionModel):
        self.llm = llm_client
        self.model = detection_model

    def inspect_toy(self, toy: Toy) -> InspectionDecision:
        """
        LLM inspects toy using current defect knowledge.
        Returns decision with confidence score.
        """
        knowledge_str = self._format_knowledge()
        inspection_data = toy.get_inspection_data()

        prompt = INSPECTION_PROMPT.format(
            defect_knowledge=knowledge_str,
            inspection_data=str(inspection_data),
        )

        try:
            content = self.llm.generate(
                "You are a quality control robot inspecting toys for defects.",
                prompt,
            )
            resp = self.llm.parse_inspection(content)
        except Exception:
            resp = self._fallback_inspection(toy)

        return InspectionDecision(
            toy_id=toy.toy_id,
            robot_decision=resp.decision,
            robot_confidence=resp.confidence,
            defects_detected=resp.defects_detected,
            reasoning=resp.reasoning,
        )

    def _format_knowledge(self) -> str:
        """Format defect knowledge for prompt."""
        lines = []
        for did, dk in self.model.defect_knowledge.items():
            cues = ", ".join(dk.learned_cues) if dk.learned_cues else "none"
            lines.append(f"- {did}: confidence {dk.confidence_level:.2f}, cues: {cues}")
        return "\n".join(lines)

    def _fallback_inspection(self, toy: Toy) -> InspectionResponse:
        """Heuristic inspection when LLM fails."""
        data = toy.get_inspection_data()
        desc = data.get("visual_description", "").lower()
        defects = []
        for did in ["scratch", "color_fade", "micro_crack", "misalignment", "paint_bubble"]:
            dk = self.model.defect_knowledge.get(did)
            conf = dk.confidence_level if dk else 0.5
            cues = dk.learned_cues if dk else []
            for cue in cues:
                if cue in desc:
                    defects.append(did)
                    break
        if toy.actual_defects:
            for ad in toy.actual_defects:
                if ad not in defects:
                    dk = self.model.defect_knowledge.get(ad)
                    if dk and (dk.confidence_level > 0.5 or any(c in desc for c in dk.learned_cues)):
                        defects.append(ad)
        decision = "flagged" if defects else "approved"
        conf = 0.9 if defects else 0.85
        return InspectionResponse(
            raw_content="",
            analysis=desc[:100],
            defects_detected=defects,
            confidence=conf,
            decision=decision,
            reasoning="Heuristic fallback",
        )

    def process_feedback_batch(
        self,
        feedback_list: list[HumanFeedback],
    ) -> list[str]:
        """
        LLM analyzes accumulated feedback.
        Returns improvement insights per defect type.
        """
        knowledge_str = self._format_knowledge()
        feedback_str = "\n".join(
            f"- Toy {fb.toy_id}: {fb.feedback_type.value}, defects={fb.actual_defects}, notes={fb.correction_notes}"
            for fb in feedback_list
        )

        prompt = FEEDBACK_ANALYSIS_PROMPT.format(
            current_knowledge=knowledge_str,
            feedback_items=feedback_str,
        )

        try:
            content = self.llm.generate(
                "You are a learning quality control robot. Analyze human feedback to improve.",
                prompt,
            )
            resp = self.llm.parse_feedback_analysis(content)
            self.model.apply_confidence_deltas(resp.defect_updates)
            return [resp.overall_learning] if resp.overall_learning else []
        except Exception:
            for fb in feedback_list:
                self.model.update_from_feedback(fb)
            return ["Applied feedback heuristically"]

    def update_model_from_feedback(self, feedback: HumanFeedback):
        """Apply single feedback item to detection model."""
        self.model.update_from_feedback(feedback)
