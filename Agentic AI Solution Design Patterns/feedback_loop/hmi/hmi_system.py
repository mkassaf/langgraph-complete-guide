"""
Human-Machine Interface for quality control.

Allows human workers to see robot decisions, flag missed defects,
confirm correct detections, and feed corrections back to the robot.
"""

from datetime import datetime

from hmi.feedback_record import (
    HumanFeedback,
    InspectionDecision,
    FeedbackSummary,
    FeedbackType,
)


class HMISystem:
    """
    Human-Machine Interface for quality control.

    Allows human workers to:
    1. See robot inspection decisions
    2. Flag missed defects (false negatives)
    3. Confirm correct detections (true positives)
    4. Review flagged items

    Continuously feeds corrections back to robot.
    """

    def __init__(self):
        self.feedback_log: list[HumanFeedback] = []
        self.pending_reviews: list[InspectionDecision] = []
        self._feedback_counter = 0

    def receive_robot_decision(self, decision: InspectionDecision, toy: Toy):
        """Robot sends its inspection decision to HMI."""
        self.pending_reviews.append(decision)

    def human_spots_missed_defect(
        self,
        toy: Toy,
        robot_decision: InspectionDecision,
        notes: str = "",
    ) -> HumanFeedback:
        """
        Human worker finds defect robot missed.
        Returns FALSE_NEGATIVE feedback.
        """
        self._feedback_counter += 1
        fb = HumanFeedback(
            feedback_id=f"fb_{self._feedback_counter}",
            toy_id=toy.toy_id,
            feedback_type=FeedbackType.FALSE_NEGATIVE,
            robot_decision=robot_decision.robot_decision,
            human_verdict="defective",
            actual_defects=toy.actual_defects,
            correction_notes=notes or f"Toy had {', '.join(toy.actual_defects)} - missed it",
            timestamp=datetime.now().isoformat(),
        )
        self.feedback_log.append(fb)
        return fb

    def human_confirms_detection(
        self,
        toy: Toy,
        robot_decision: InspectionDecision,
    ) -> HumanFeedback:
        """
        Human confirms robot correctly flagged a defect.
        Returns TRUE_POSITIVE feedback.
        """
        self._feedback_counter += 1
        fb = HumanFeedback(
            feedback_id=f"fb_{self._feedback_counter}",
            toy_id=toy.toy_id,
            feedback_type=FeedbackType.TRUE_POSITIVE,
            robot_decision=robot_decision.robot_decision,
            human_verdict="defective",
            actual_defects=toy.actual_defects,
            correction_notes="Confirmed, good catch!",
            timestamp=datetime.now().isoformat(),
        )
        self.feedback_log.append(fb)
        return fb

    def human_corrects_false_positive(
        self,
        toy: Toy,
        robot_decision: InspectionDecision,
        notes: str = "No defect found on manual inspection",
    ) -> HumanFeedback:
        """Human says robot wrongly flagged - no defect."""
        self._feedback_counter += 1
        fb = HumanFeedback(
            feedback_id=f"fb_{self._feedback_counter}",
            toy_id=toy.toy_id,
            feedback_type=FeedbackType.FALSE_POSITIVE,
            robot_decision=robot_decision.robot_decision,
            human_verdict="acceptable",
            actual_defects=[],
            correction_notes=notes,
            timestamp=datetime.now().isoformat(),
        )
        self.feedback_log.append(fb)
        return fb

    def human_confirms_acceptable(
        self,
        toy: Toy,
        robot_decision: InspectionDecision,
    ) -> HumanFeedback:
        """Human confirms robot correctly approved (true negative)."""
        self._feedback_counter += 1
        fb = HumanFeedback(
            feedback_id=f"fb_{self._feedback_counter}",
            toy_id=toy.toy_id,
            feedback_type=FeedbackType.TRUE_NEGATIVE,
            robot_decision=robot_decision.robot_decision,
            human_verdict="acceptable",
            actual_defects=[],
            correction_notes="Correct - no defect",
            timestamp=datetime.now().isoformat(),
        )
        self.feedback_log.append(fb)
        return fb

    def get_pending_feedback(self) -> list[HumanFeedback]:
        """Get all unprocessed feedback for robot."""
        return list(self.feedback_log)

    def get_feedback_summary(
        self,
        decisions: list[InspectionDecision],
        toys: dict[str, Toy],
    ) -> FeedbackSummary:
        """Calculate accuracy metrics from decisions vs ground truth."""
        fn = tp = fp = tn = 0
        for dec in decisions:
            toy = toys.get(dec.toy_id)
            if not toy:
                continue
            robot_flag = dec.robot_decision == "flagged"
            actual_defect = toy.is_defective

            if actual_defect and robot_flag:
                tp += 1
            elif actual_defect and not robot_flag:
                fn += 1
            elif not actual_defect and robot_flag:
                fp += 1
            else:
                tn += 1

        total = tp + fn + fp + tn
        accuracy = (tp + tn) / total if total else 0.0
        defect_total = tp + fn
        detection_rate = tp / defect_total if defect_total else 0.0

        return FeedbackSummary(
            total_inspections=total,
            false_negatives=fn,
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            accuracy=accuracy,
            detection_rate=detection_rate,
        )

    def simulate_human_review(
        self,
        decisions: list[InspectionDecision],
        toys: dict[str, Toy],
    ) -> list[HumanFeedback]:
        """
        Simulate human reviewing a batch of robot decisions.
        Automatically generates appropriate feedback based on
        ground truth vs robot decisions.
        """
        feedback_list: list[HumanFeedback] = []
        for dec in decisions:
            toy = toys.get(dec.toy_id)
            if not toy:
                continue
            robot_flag = dec.robot_decision == "flagged"
            actual_defect = toy.is_defective

            if actual_defect and robot_flag:
                feedback_list.append(self.human_confirms_detection(toy, dec))
            elif actual_defect and not robot_flag:
                defect_str = ", ".join(toy.actual_defects)
                feedback_list.append(
                    self.human_spots_missed_defect(
                        toy,
                        dec,
                        notes=f"Toy had {defect_str} - missed it",
                    )
                )
            elif not actual_defect and robot_flag:
                feedback_list.append(self.human_corrects_false_positive(toy, dec))
            else:
                feedback_list.append(self.human_confirms_acceptable(toy, dec))
        return feedback_list
