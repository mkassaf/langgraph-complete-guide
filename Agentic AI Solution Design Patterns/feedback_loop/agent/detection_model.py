"""
Robot's defect detection model.
Starts with basic knowledge, improves with human feedback.
"""

from dataclasses import dataclass
from datetime import datetime

from hmi.feedback_record import HumanFeedback, FeedbackType
from factory.defect_types import DEFECT_TYPES


@dataclass
class DefectKnowledge:
    defect_id: str
    confidence_level: float
    detection_count: int
    miss_count: int
    last_updated: str
    learned_cues: list[str]


class DefectDetectionModel:
    """
    Robot's internal model for defect detection.
    Starts with basic knowledge, improves with feedback.

    Tracks confidence per defect type.
    Updates based on human corrections and confirmations.
    """

    def __init__(self):
        self.defect_knowledge: dict[str, DefectKnowledge] = {
            "scratch": DefectKnowledge(
                "scratch", 0.90, 0, 0, "initial", ["linear mark"]
            ),
            "color_fade": DefectKnowledge(
                "color_fade", 0.50, 0, 0, "initial", ["uneven color"]
            ),
            "micro_crack": DefectKnowledge(
                "micro_crack", 0.20, 0, 0, "initial", []
            ),
            "misalignment": DefectKnowledge(
                "misalignment", 0.45, 0, 0, "initial", ["gap"]
            ),
            "paint_bubble": DefectKnowledge(
                "paint_bubble", 0.15, 0, 0, "initial", []
            ),
        }

    def get_confidence(self, defect_id: str) -> float:
        """Get current confidence for detecting a defect type."""
        dk = self.defect_knowledge.get(defect_id)
        return dk.confidence_level if dk else 0.5

    def update_from_feedback(self, feedback: HumanFeedback):
        """
        Update model based on human feedback.
        False negative → increase confidence (we're learning), add cues
        True positive → increase confidence
        """
        now = datetime.now().isoformat()
        for defect_id in feedback.actual_defects:
            dk = self.defect_knowledge.get(defect_id)
            if not dk:
                continue

            if feedback.feedback_type == FeedbackType.FALSE_NEGATIVE:
                dk.miss_count += 1
                dk.confidence_level = min(0.95, dk.confidence_level + 0.2)
                dt = DEFECT_TYPES.get(defect_id)
                if dt:
                    for cue in dt.visual_cues:
                        if cue not in dk.learned_cues:
                            dk.learned_cues.append(cue)
                dk.last_updated = now

            elif feedback.feedback_type == FeedbackType.TRUE_POSITIVE:
                dk.detection_count += 1
                dk.confidence_level = min(0.95, dk.confidence_level + 0.05)
                dk.last_updated = now

    def apply_confidence_deltas(self, defect_updates: dict[str, dict]):
        """Apply confidence deltas and new cues from LLM feedback analysis."""
        now = datetime.now().isoformat()
        for defect_id, updates in defect_updates.items():
            dk = self.defect_knowledge.get(defect_id)
            if not dk:
                continue
            delta = updates.get("confidence_delta", 0)
            dk.confidence_level = max(0.1, min(0.95, dk.confidence_level + delta))
            for cue in updates.get("new_cues", []):
                if cue and cue not in dk.learned_cues:
                    dk.learned_cues.append(cue)
            dk.last_updated = now

    def get_model_summary(self) -> dict:
        """Summary of current detection capabilities per defect."""
        return {
            did: {
                "confidence": dk.confidence_level,
                "cues": dk.learned_cues,
            }
            for did, dk in self.defect_knowledge.items()
        }
