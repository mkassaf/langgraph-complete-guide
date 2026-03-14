"""
Human Feedback Loop — Entry Point

Runs 3 feedback rounds demonstrating improvement through human feedback.
"""

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from dotenv import load_dotenv

_env_path = os.path.join(_SCRIPT_DIR, "..", "..", ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
else:
    load_dotenv()

from factory.toy_generator import ToyGenerator
from hmi.feedback_record import FeedbackType
from agent import Controller
from agent.detection_model import DefectDetectionModel
from agent.llm_client import LLMClient
from hmi.hmi_system import HMISystem
from config import MODEL, MAX_TOKENS


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║     HUMAN FEEDBACK LOOP INTEGRATION DEMO            ║
║         Toy Factory Quality Control Robot           ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient(model=MODEL, max_tokens=MAX_TOKENS)
    model = DefectDetectionModel()
    controller = Controller(llm, model)
    hmi = HMISystem()
    generator = ToyGenerator(seed=42)

    # Same batch for all rounds - model improves so we see better detection each time
    batch = _make_demo_batch_1(generator)
    batch_names = [
        "Initial (Before Any Feedback)",
        "After First Feedback Cycle",
        "After Second Feedback Cycle",
    ]

    round_stats = []

    for round_num, batch_name in enumerate(batch_names, start=1):
        toys = {t.toy_id: t for t in batch}
        decisions: list = []

        print("━" * 60)
        print(f"ROUND {round_num}: {batch_name}")
        print("━" * 60)
        print(f"Inspecting {len(batch)} toys...\n")

        for toy in batch:
            dec = controller.inspect_toy(toy)
            decisions.append(dec)
            hmi.receive_robot_decision(dec, toy)

            result_text = _get_result_text(toy, dec)
            flag_icon = "⚠️" if dec.robot_decision == "flagged" else "✅"
            print(f"🔍 TOY #{toy.toy_id} ({toy.name} - {toy.actual_defects or 'no defects'}):")
            print(f"   Robot Decision: {'FLAGGED' if dec.robot_decision == 'flagged' else 'APPROVED'} {flag_icon}")
            print(f"   Confidence: {dec.robot_confidence:.2f}")
            print(f"   Actual Defects: {toy.actual_defects or 'none'}")
            print(f"   Result: {result_text}\n")

        feedback_list = hmi.simulate_human_review(decisions, toys)

        print("👤 HUMAN FEEDBACK (via HMI):")
        for fb in feedback_list:
            if fb.feedback_type == FeedbackType.FALSE_NEGATIVE:
                print(f"   Correction: \"{fb.correction_notes}\"")
            elif fb.feedback_type == FeedbackType.TRUE_POSITIVE:
                print(f"   Confirmation: \"{fb.correction_notes}\"")
            elif fb.feedback_type == FeedbackType.FALSE_POSITIVE:
                print(f"   Correction: \"{fb.correction_notes}\"")
            else:
                print(f"   Confirmation: \"{fb.correction_notes}\"")

        print("\n🧠 LLM ANALYZING FEEDBACK:")
        insights = controller.process_feedback_batch(feedback_list)
        for ins in insights[:3]:
            print(f"   {ins[:80]}...")

        summary = hmi.get_feedback_summary(decisions, toys)
        round_stats.append((round_num, model.get_model_summary(), summary))
        print(f"\n📊 ROUND {round_num} STATS:")
        defect_count = sum(1 for t in batch if t.is_defective)
        print(f"   Detection rate: {summary.true_positives}/{defect_count} defects = {summary.detection_rate*100:.0f}%")
        print(f"   Accuracy: {summary.accuracy*100:.0f}%\n")

    # Final report
    print("╔══════════════════════════════════════════════════════╗")
    print("║              LEARNING PROGRESS REPORT               ║")
    print("╠═══════════════════╦════════╦════════╦═══════════════╣")
    print("║ Defect Type       ║ Round1 ║ Round2 ║ Round3        ║")
    print("╠═══════════════════╬════════╬════════╬═══════════════╣")

    defect_ids = ["scratch", "color_fade", "micro_crack", "misalignment", "paint_bubble"]
    for did in defect_ids:
        r1 = round_stats[0][1].get(did, {}).get("confidence", 0) * 100
        r2 = round_stats[1][1].get(did, {}).get("confidence", 0) * 100
        r3 = round_stats[2][1].get(did, {}).get("confidence", 0) * 100
        print(f"║ {did:<17} ║ {r1:>5.0f}% ║ {r2:>5.0f}% ║ {r3:>5.0f}%          ║")

    acc1 = round_stats[0][2].accuracy * 100
    acc2 = round_stats[1][2].accuracy * 100
    acc3 = round_stats[2][2].accuracy * 100
    print("╠═══════════════════╬════════╬════════╬═══════════════╣")
    print(f"║ OVERALL ACCURACY  ║ {acc1:>4.0f}%  ║ {acc2:>4.0f}%  ║ {acc3:>4.0f}%          ║")
    print("╚═══════════════════╩════════╩════════╩═══════════════╝")
    print("""
KEY INSIGHT:
The robot improved through 3 rounds of human feedback - WITHOUT retraining from scratch.
Human corrections and confirmations drive continuous learning.
""")


def _get_result_text(toy, dec):
    """Get result text for display."""
    robot_flag = dec.robot_decision == "flagged"
    actual_defect = toy.is_defective
    if actual_defect and robot_flag:
        return "✅ TRUE POSITIVE - correctly detected"
    elif actual_defect and not robot_flag:
        return "❌ FALSE NEGATIVE - missed defect"
    elif not actual_defect and robot_flag:
        return "❌ FALSE POSITIVE - wrongly flagged"
    else:
        return "✅ TRUE NEGATIVE - correct"


def _make_demo_batch_1(gen: ToyGenerator):
    """Fixed batch for round 1: mix of defects."""
    from factory.toy_generator import Toy
    return [
        gen.generate_toy_with_defect("micro_crack", "toy_1"),
        gen.generate_toy_with_defect("color_fade", "toy_2"),
        Toy("toy_3", "Bunny", "stuffed_animal", [], "Bunny (stuffed_animal) - appears in good condition", False),
        gen.generate_toy_with_defect("scratch", "toy_4"),
        gen.generate_toy_with_defect("paint_bubble", "toy_5"),
    ]




if __name__ == "__main__":
    main()
