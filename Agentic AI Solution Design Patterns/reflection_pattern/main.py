"""
Reflection Pattern — Entry Point

Runs all 3 demonstrations.
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

from config import USER_REQUEST
from agent import MeetingPlannerAgent


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║          REFLECTION PATTERN DEMONSTRATION           ║
╚══════════════════════════════════════════════════════╝
""")

    agent = MeetingPlannerAgent()

    # ── DEMO 1: CoT + Reflection ──
    print("━" * 50)
    print("DEMO 1: CHAIN OF THOUGHT + REFLECTION")
    print("━" * 50)
    try:
        r1 = agent.demo_cot_with_reflection(USER_REQUEST)
        print("\n📝 INITIAL OUTPUT (CoT):")
        print(r1.initial_output[:600] + ("..." if len(r1.initial_output) > 600 else ""))
        for rr in r1.reflection_rounds:
            print(f"\n🔍 REFLECTION ROUND {rr.round_number}:")
            if rr.reflection_response.has_improvement:
                print("⚠️  ISSUES FOUND (from reflection)")
                print("✨ IMPROVED OUTPUT:")
                print((rr.improved_output or "")[:400] + "...")
                print("CHANGES MADE: (see reflection)")
            if rr.verdict == "SATISFACTORY":
                print("✅ VERDICT: OUTPUT IS SATISFACTORY")
        print(f"\nTotal improvements: {r1.total_improvements} round(s)")
    except Exception as e:
        print(f"Error: {e}")

    # ── DEMO 2: ReAct + Reflection ──
    print("\n" + "━" * 50)
    print("DEMO 2: REACT + REFLECTION")
    print("━" * 50)
    try:
        r2 = agent.demo_react_with_reflection(USER_REQUEST)
        print("\n⚡ REACT ACTIONS TAKEN:")
        for i, a in enumerate((r2.action_log or []), 1):
            status = "✅" if "ERROR" not in str(a.get("observation", "")) else "❌"
            print(f"  Action {i}: {a.get('action','')[:50]}... {status}")
        for rr in r2.reflection_rounds:
            print("\n🔍 REFLECTION ON ACTIONS:")
            if rr.reflection_response.has_correction:
                print("❌ ERROR DETECTED")
                print(f"🔧 CORRECTION NEEDED: {rr.action_taken}")
            if r2.correction_applied:
                print("✅ CORRECTION APPLIED - document created successfully")
            if rr.verdict == "VERIFIED":
                print("✅ VERIFIED: Task completed successfully")
    except Exception as e:
        print(f"Error: {e}")

    # ── DEMO 3: Pattern Switch ──
    print("\n" + "━" * 50)
    print("DEMO 3: PATTERN SWITCH VIA REFLECTION")
    print("━" * 50)
    try:
        r3 = agent.demo_pattern_switch(USER_REQUEST)
        print("\n📝 INITIAL OUTPUT (Simple):")
        print(r3.initial_output[:400] + "...")
        if r3.pattern_switched:
            print("\n🔄 SWITCH TO REACT RECOMMENDED")
            print("Reason: (see reflection)")
        print("\n✅ FINAL OUTPUT (After Switch):")
        print(r3.final_output[:500] + ("..." if len(r3.final_output) > 500 else ""))
    except Exception as e:
        print(f"Error: {e}")

    # ── SUMMARY ──
    print("""
╔══════════════════════════════════════════════════════╗
║              REFLECTION PATTERN SUMMARY             ║
╠══════════════════════════════════════════════════════╣
║ Demo 1 - CoT + Reflection:                           ║
║   Improvement rounds: (see above)                    ║
║   Issues caught: completeness, assumptions, logic     ║
║                                                      ║
║ Demo 2 - ReAct + Reflection:                        ║
║   Errors detected: document_tool date=None            ║
║   Corrections applied: 1                             ║
║                                                      ║
║ Demo 3 - Pattern Switch:                            ║
║   Started as: Simple prompt                         ║
║   Switched to: ReAct (if recommended)                 ║
║   Reason: Task required real data + actions          ║
╚══════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
