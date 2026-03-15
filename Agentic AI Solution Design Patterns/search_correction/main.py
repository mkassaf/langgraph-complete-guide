"""
Search and Self-Correction Patterns — 3 Patterns, Same Meeting Task

Organize a half-day team meeting for 15 people in 3 weeks.
Each pattern handles errors and finds optimal solutions differently.
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

from config import TASK, MCTS_ITERATIONS
from llm_client import LLMClient
from tools import TOOLS
from patterns.lats_pattern import LATSPattern
from patterns.self_discover_pattern import SelfDiscoverPattern
from patterns.second_pass_verification import SecondPassVerification


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║    SEARCH AND SELF-CORRECTION PATTERNS DEMO         ║
║         3 Patterns - Same Meeting Task              ║
╚══════════════════════════════════════════════════════╝
""")

    task = TASK.strip()
    print("TASK:", task[:70] + "...")
    print()

    # ━━━ PATTERN 1: LATS ━━━
    print("━" * 60)
    print("PATTERN 1: LANGUAGE AGENT TREE SEARCH (LATS)")
    print("━" * 60)
    llm1 = LLMClient()
    lats = LATSPattern(llm1, TOOLS, mcts_iterations=MCTS_ITERATIONS)
    r1 = lats.run(task)

    # ━━━ PATTERN 2: Self-Discover ━━━
    print("\n" + "━" * 60)
    print("PATTERN 2: SELF-DISCOVER")
    print("━" * 60)
    llm2 = LLMClient()
    sd = SelfDiscoverPattern(llm2, TOOLS)
    r2 = sd.run(task)

    # ━━━ PATTERN 3: Second-Pass Verification ━━━
    print("\n" + "━" * 60)
    print("PATTERN 3: SECOND-PASS VERIFICATION")
    print("━" * 60)
    planner_llm = LLMClient()
    verifier_llm = LLMClient()
    v = SecondPassVerification(planner_llm, verifier_llm, TOOLS)
    r3 = v.run(task)

    # ━━━ COMPARISON ━━━
    print("\n" + "━" * 60)
    print("PATTERNS COMPARISON")
    print("━" * 60)
    print("""
╔════════════════╦══════════╦═════════════╦════════════╗
║ Metric         ║ LATS     ║ Self-Disc.  ║ Verif.     ║
╠════════════════╬══════════╬═════════════╬════════════╣
║ LLM calls      ║ Many     ║ 2 stages    ║ 3+ (P+V+P) ║
║ Error found    ║ Avoided  ║ Rules prev. ║ Caught+fix ║
║ Approach       ║ Explore  ║ Strategy    ║ Audit      ║
║ Best for       ║ Complex  ║ Novel tasks ║ High-stakes║
╚════════════════╩══════════╩═════════════╩════════════╝
""")


if __name__ == "__main__":
    main()
