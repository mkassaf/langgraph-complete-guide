"""
Chain of Thought — Entry Point

Runs the full demonstration comparing standard vs CoT prompting.
"""

import os
import sys

# Ensure package imports work when run from project root or chain_of_thought dir
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from dotenv import load_dotenv

# Load .env from project root (parent of Agentic AI Solution Design Patterns)
_env_path = os.path.join(_SCRIPT_DIR, "..", "..", ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
else:
    load_dotenv()

from config import USER_REQUEST
from agent import EventPlanningAgent
from comparator import ChainOfThoughtComparator


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        print("Get a key at: https://console.anthropic.com/")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║         CHAIN OF THOUGHT PATTERN DEMO                ║
║         Event Planning Agent Comparison              ║
╚══════════════════════════════════════════════════════╝
""")

    print(f"USER REQUEST:\n{USER_REQUEST}\n")

    agent = EventPlanningAgent()
    comparator = ChainOfThoughtComparator(agent)

    try:
        report = comparator.run_comparison(USER_REQUEST)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    # Mode 1: WITHOUT Chain of Thought
    print("=" * 60)
    print("MODE 1: WITHOUT CHAIN OF THOUGHT")
    print("=" * 60)
    print(report.without_cot.llm_response.content[:1500])
    if len(report.without_cot.llm_response.content) > 1500:
        print("\n[... truncated ...]")
    print("\n--- Issues detected ---")
    for issue in report.without_cot.issues_detected:
        print(f"  • {issue}")
    if report.without_cot.assumptions_made:
        print("--- Assumptions made ---")
        for a in report.without_cot.assumptions_made[:5]:
            print(f"  • {a[:80]}...")

    # Mode 2: WITH Chain of Thought
    print("\n" + "=" * 60)
    print("MODE 2: WITH CHAIN OF THOUGHT")
    print("=" * 60)
    if report.with_cot.llm_response.reasoning_steps:
        for i, step in enumerate(report.with_cot.llm_response.reasoning_steps, 1):
            print(f"\n--- THOUGHT {i} ---")
            print(step[:400] + ("..." if len(step) > 400 else ""))
    else:
        print(report.with_cot.llm_response.content[:1500])
        if len(report.with_cot.llm_response.content) > 1500:
            print("\n[... truncated ...]")
    print("\n--- Final recommendation ---")
    # Last part of content is usually the conclusion
    content = report.with_cot.llm_response.content
    if "CONCLUDE" in content.upper() or "THOUGHT 4" in content.upper():
        parts = content.upper().split("THOUGHT 4") if "THOUGHT 4" in content.upper() else content.split("CONCLUDE")
        if len(parts) > 1:
            print(parts[-1].strip()[:800])
        else:
            print(content[-800:])
    else:
        print(content[-600:])
    if report.with_cot.assumptions_made:
        print("\n--- Assumptions made ---")
        for a in report.with_cot.assumptions_made[:3]:
            print(f"  • {a[:80]}...")

    # Comparison table
    w = report.without_cot_analysis
    c = report.with_cot_analysis
    wo = report.without_cot.llm_response
    wi = report.with_cot.llm_response

    print("""
╔══════════════════════════════════════════════════════╗
║                COMPARISON SUMMARY                   ║
╠══════════════════════════════════════╦═══════════╦══════╣
║ Metric                               ║ Standard  ║ CoT  ║
╠══════════════════════════════════════╬═══════════╬══════╣""")
    print(f"║ Assumptions made                  │ {w.assumptions_count:^9} │ {c.assumptions_count:^4} ║")
    print(f"║ Missing considerations            │ {len(w.missing_considerations):^9} │ {len(c.missing_considerations):^4} ║")
    print(f"║ Reasoning steps visible            │ {w.reasoning_steps_count:^9} │ {c.reasoning_steps_count:^4} ║")
    print(f"║ Specificity score (1-10)          │ {w.specificity_score:^9} │ {c.specificity_score:^4} ║")
    print(f"║ Tokens used                       │ {wo.tokens_used:^9} │ {wi.tokens_used:^4} ║")
    print("""╚══════════════════════════════════════╩═══════════╩══════╝

KEY INSIGHT:
CoT uses more tokens but produces significantly better
reasoning for complex multi-step tasks.
Standard mode is fine for simple queries.
""")


if __name__ == "__main__":
    main()
