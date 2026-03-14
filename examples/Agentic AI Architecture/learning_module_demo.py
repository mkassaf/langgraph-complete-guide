"""
Learning Module Demo — Storing Feedback, Improving Over Time

Demonstrates how the learning module:
- Stores feedback from the environment
- Analyzes what worked and what didn't
- Refines behavior (reasoning, action) based on feedback
- Improves perception, reasoning, and action over time

Run from project root:
    python examples/"Agentic AI Architecture"/learning_module_demo.py
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import sys
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))


# ─── Warehouse Robot Scenario (from transcript) ──────────────────────────────

class DoorSolution(Enum):
    """Solutions for locked door situation."""
    TEXT_HUMAN = "text_human"
    ENTER_KEYPAD = "enter_keypad"


@dataclass
class FeedbackEntry:
    """Single feedback event from the environment."""
    source: str  # human, supervisor, monitor, other_robot
    situation: str
    solution_used: str
    message: str
    positive: bool  # True = worked well, False = problem


class LearningModule:
    """
    Learning module: stores feedback, identifies patterns, proposes improvements.
    """

    def __init__(self):
        self.feedback_log: list[FeedbackEntry] = []
        self.learned_rules: dict = {}

    def store_feedback(self, feedback: FeedbackEntry):
        """Store feedback from environment (human, monitors, etc.)."""
        self.feedback_log.append(feedback)

    def analyze_feedback(self, situation: str) -> dict:
        """
        Analyze stored feedback for a situation.
        Returns: patterns, recommended solution, reasoning.
        """
        relevant = [f for f in self.feedback_log if f.situation == situation]
        positive = [f for f in relevant if f.positive]
        negative = [f for f in relevant if not f.positive]

        # Pattern: if text_human has many negative feedbacks, learn alternative
        text_human_negative = [f for f in negative if f.solution_used == DoorSolution.TEXT_HUMAN.value]

        if len(text_human_negative) >= 2:  # Threshold: learned from repeated feedback
            return {
                "situation": situation,
                "pattern": "text_human causes delays and human dissatisfaction",
                "recommended_solution": DoorSolution.ENTER_KEYPAD.value,
                "reason": "Feedback indicates keypad solution is faster and preferred",
                "feedback_count": len(relevant),
            }
        return {
            "situation": situation,
            "pattern": "Insufficient feedback to change",
            "recommended_solution": DoorSolution.TEXT_HUMAN.value,
            "reason": "Default: use human assistance",
            "feedback_count": len(relevant),
        }

    def update_rule(self, rule_name: str, new_value: str):
        """Refine predefined rule based on learning."""
        self.learned_rules[rule_name] = new_value


# ─── Demo 1: Warehouse Robot Learning ────────────────────────────────────────

def run_warehouse_robot_learning():
    """Locked door scenario: learn from feedback, switch from text_human to keypad."""
    print("=" * 65)
    print("LEARNING MODULE — Warehouse Robot (Locked Door)")
    print("=" * 65)

    learning = LearningModule()

    print("\n1. INITIAL BEHAVIOR: Robot texts human when door is locked")
    print("   Solution: text_human")

    print("\n2. FEEDBACK RECEIVED (stored by learning module)")
    feedbacks = [
        FeedbackEntry("human", "door_locked", "text_human", "Prefer not to run to door each time", False),
        FeedbackEntry("supervisor", "door_locked", "text_human", "Task delays unacceptable", False),
        FeedbackEntry("monitor", "door_locked", "text_human", "Delivery time exceeded allocation", False),
        FeedbackEntry("monitor", "door_locked", "text_human", "Queued tasks delayed", False),
    ]
    for f in feedbacks:
        learning.store_feedback(f)
        print(f"   [{f.source}] {f.message}")

    print("\n3. LEARNING MODULE ANALYZES FEEDBACK")
    analysis = learning.analyze_feedback("door_locked")
    print(f"   Pattern: {analysis['pattern']}")
    print(f"   Feedback count: {analysis['feedback_count']}")

    print("\n4. LEARNING MODULE UPDATES REASONING RULE")
    learning.update_rule("door_locked_solution", DoorSolution.ENTER_KEYPAD.value)
    print(f"   Rule: door_locked_solution = {learning.learned_rules['door_locked_solution']}")

    print("\n5. NEW BEHAVIOR: Robot uses keypad when door is locked")
    print("   Solution: enter_keypad (learned from feedback)")
    print("   Outcome: Faster, no human interruption, no task delays")

    print("=" * 65)


# ─── Demo 2: Paper Screening Agent Learning ──────────────────────────────────

@dataclass
class ScreeningFeedback:
    """Feedback on paper screening decision."""
    arxiv_id: str
    agent_decision: str  # Include/Exclude
    manual_decision: str
    reason: str  # Why manual disagreed


def run_paper_screening_learning():
    """Learn from manual review disagreements to improve criterion application."""
    print("\n" + "=" * 65)
    print("LEARNING MODULE — Paper Screening Agent")
    print("=" * 65)

    # Simulated feedback from manual review comparison
    feedbacks = [
        ScreeningFeedback("2601.16530v1", "Include", "Exclude", "Agentic loop is training pipeline, not inference"),
        ScreeningFeedback("2601.09694v1", "Include", "Exclude", "Cost metrics refer to pruned model, not agent"),
        ScreeningFeedback("2601.05505v1", "Include", "Exclude", "Single-turn benchmarks, not agentic"),
    ]

    print("\n1. FEEDBACK: Manual review disagrees with agent")
    for f in feedbacks:
        print(f"   {f.arxiv_id}: Agent={f.agent_decision}, Manual={f.manual_decision}")
        print(f"      Reason: {f.reason}")

    print("\n2. LEARNING MODULE IDENTIFIES PATTERNS")
    patterns = [
        "Training-time agentic → should EXCLUDE (E2)",
        "Efficiency of target system, not agent → should EXCLUDE (E3)",
        "Single-turn, no tool use → should EXCLUDE (E2)",
    ]
    for p in patterns:
        print(f"   • {p}")

    print("\n3. LEARNING MODULE REFINES REASONING")
    print("   Update E2 criterion: Add 'agentic at inference time' requirement")
    print("   Update reflection: Flag training/data-curation pipelines")
    print("   Update E3: Distinguish 'agent efficiency' vs 'target system efficiency'")

    print("\n4. LEARNING MODULE REFINES PERCEPTION (hypothetical)")
    print("   Improve title extraction: Skip 'Preprint - Under Peer Review'")
    print("   Tag paper type from abstract: training vs inference focus")

    print("\n5. RESULT: Fewer false includes, better alignment with manual review")
    print("=" * 65)


# ─── Demo 3: Learning Module + All Modules ───────────────────────────────────

def run_integration_summary():
    """Summary of how learning interacts with perception, reasoning, action."""
    print("\n" + "=" * 65)
    print("LEARNING MODULE — Integration with Other Modules")
    print("=" * 65)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│ LEARNING + PERCEPTION                                            │
│ • Analyze percepts, identify errors in extraction                │
│ • Refine: feature extraction, object recognition, noise filtering│
│ • Goal: Better quality perceptions → Reasoning                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ LEARNING + REASONING                                             │
│ • Observe planning, decisions, outcomes                           │
│ • Adjust: decision rules, heuristics, goals                       │
│ • Example: Add rule for 'agentic at inference time only'         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ LEARNING + ACTION                                               │
│ • Analyze actions → environmental consequences                   │
│ • Refine: effector effectiveness, precision, efficiency         │
│ • Develop: new skills (e.g., keypad entry for robot)            │
└─────────────────────────────────────────────────────────────────┘
""")
    print("=" * 65)


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_warehouse_robot_learning()
    run_paper_screening_learning()
    run_integration_summary()
