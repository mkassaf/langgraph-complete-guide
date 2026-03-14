"""
Feedback data structures for Human-Machine Interface.
"""

from enum import Enum
from dataclasses import dataclass


class FeedbackType(Enum):
    FALSE_NEGATIVE = "false_negative"  # Robot missed a defect
    TRUE_POSITIVE = "true_positive"  # Robot correctly flagged
    FALSE_POSITIVE = "false_positive"  # Robot wrongly flagged
    TRUE_NEGATIVE = "true_negative"  # Robot correctly approved


@dataclass
class InspectionDecision:
    toy_id: str
    robot_decision: str  # "approved" | "flagged"
    robot_confidence: float  # 0.0 to 1.0
    defects_detected: list[str]
    reasoning: str


@dataclass
class HumanFeedback:
    feedback_id: str
    toy_id: str
    feedback_type: FeedbackType
    robot_decision: str
    human_verdict: str  # "defective" | "acceptable"
    actual_defects: list[str]
    correction_notes: str  # Human's explanation
    timestamp: str


@dataclass
class FeedbackSummary:
    total_inspections: int
    false_negatives: int  # Missed defects
    true_positives: int  # Correctly flagged
    false_positives: int  # Wrong flags
    true_negatives: int  # Correctly approved
    accuracy: float
    detection_rate: float  # true_pos / (true_pos + false_neg)
