"""
ReAct Pattern — Entry Point

Runs the full ReAct demonstration.
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


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        print("Get a key at: https://console.anthropic.com/")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║           ReAct PATTERN DEMONSTRATION               ║
║         Meeting Planner Agent in Action             ║
╚══════════════════════════════════════════════════════╝
""")

    print("USER REQUEST:")
    print(USER_REQUEST)
    print()

    agent = MeetingPlannerAgent()

    try:
        result = agent.plan_meeting(USER_REQUEST)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    for entry in result.action_log:
        it = entry.get("iteration", 0)
        print("━" * 40)
        print(f"ITERATION {it}")
        print("━" * 40)
        print("💭 THOUGHT:")
        print(entry.get("thought", "")[:500])
        if len(entry.get("thought", "")) > 500:
            print("...")
        print()
        print("⚡ ACTION:")
        print(entry.get("action", "(none)"))
        print()
        print("👁️  OBSERVATION:")
        print(entry.get("observation", ""))
        print()

    tools_used = len(set(
        a.get("action", "").split("(")[0].strip()
        for a in result.action_log
        if a.get("action") and "(" in a.get("action", "")
    ))

    print("""
╔══════════════════════════════════════════════════════╗
║                  MISSION COMPLETE                   ║
╠══════════════════════════════════════════════════════╣""")
    print(f"║ Iterations completed:  {result.iterations:<26} ║")
    print(f"║ Tools used:            {tools_used}/4{' '*24} ║")
    doc_status = "proposal.md ✅" if result.document_created else "No"
    print(f"║ Document created:     {doc_status:<26} ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ FINAL PLAN:                                           ║")
    for line in (result.final_answer or "").split("\n")[:8]:
        print(f"║ {line[:52]:<52} ║")
    print("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
