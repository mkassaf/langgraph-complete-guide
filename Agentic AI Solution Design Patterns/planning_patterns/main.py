"""
Planning & Execution Patterns — 4 Patterns, Same Meeting Task

Plan a half-day team offsite for 15 people with engaging activities and catering.
Each pattern approaches the SAME task differently.
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

from config import TASK
from llm_client import LLMClient
from tools import TOOLS
from patterns.plan_and_execute import PlanAndExecutePattern
from patterns.concurrent_optimizer import ConcurrentExecutionOptimizer
from patterns.reasoning_no_obs import ReasoningWithoutObservation
from patterns.planner_critic import PlannerCriticRefiner


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║      PLANNING & EXECUTION PATTERNS COMPARISON       ║
║         4 Patterns - Same Meeting Task              ║
╚══════════════════════════════════════════════════════╝
""")

    task = TASK.strip()
    print("TASK:", task[:80] + "...")
    print()

    results = {}

    # ━━━ PATTERN 1: Plan-and-Execute ━━━
    print("━" * 60)
    print("[P1] PATTERN 1: PLAN-AND-EXECUTE")
    print("━" * 60)
    llm1 = LLMClient()
    p1 = PlanAndExecutePattern(llm1, TOOLS)
    results["p1"] = p1.run(task)
    print(f"\n[P1] LLM calls: {results['p1']['llm_calls']} | Time: {results['p1']['elapsed']:.1f}s")

    # ━━━ PATTERN 2: Concurrent Optimizer ━━━
    print("\n" + "━" * 60)
    print("[P2] PATTERN 2: CONCURRENT EXECUTION OPTIMIZER")
    print("━" * 60)
    llm2 = LLMClient()
    p2 = ConcurrentExecutionOptimizer(llm2, TOOLS)
    results["p2"] = p2.run(task)
    print(f"\n[P2] LLM calls: {results['p2']['llm_calls']} | Time: {results['p2']['elapsed']:.1f}s")

    # ━━━ PATTERN 3: Reasoning Without Observation ━━━
    print("\n" + "━" * 60)
    print("[P3] PATTERN 3: REASONING WITHOUT OBSERVATION")
    print("━" * 60)
    llm3 = LLMClient()
    p3 = ReasoningWithoutObservation(llm3, TOOLS)
    results["p3"] = p3.run(task)
    print(f"\n[P3] LLM calls: {results['p3']['llm_calls']} | Time: {results['p3']['elapsed']:.1f}s")

    # ━━━ PATTERN 4: Planner-Critic-Refiner ━━━
    print("\n" + "━" * 60)
    print("[P4] PATTERN 4: PLANNER-CRITIC-REFINER")
    print("━" * 60)
    llm4 = LLMClient()
    p4 = PlannerCriticRefiner(
        llm4,
        TOOLS,
        max_iterations=3,
        quality_threshold=0.85,
        demo_scores=[0.52, 0.78, 0.91],
    )
    results["p4"] = p4.run(task)
    print(f"\n[P4] LLM calls: {results['p4']['llm_calls']} | Iterations: {results['p4'].get('iterations', 0)}")

    # ━━━ COMPARISON SUMMARY ━━━
    print("\n" + "━" * 60)
    print("PATTERNS COMPARISON SUMMARY")
    print("━" * 60)
    print("""
╔════════════════════╦═══════╦═══════╦═══════╦════════════╗
║ Metric            ║ P1    ║ P2    ║ P3    ║ P4         ║
╠════════════════════╬═══════╬═══════╬═══════╬════════════╣
║ LLM calls        ║  {p1:>3}  ║  {p2:>3}  ║  {p3:>3}  ║  {p4:>3}       ║
║ Parallel exec    ║  No    ║  Yes   ║  Yes   ║  No        ║
║ Plan quality     ║  Med   ║  Med   ║  Med   ║  High      ║
║ Adaptability     ║  Low   ║  Low   ║  Med   ║  Low       ║
║ Cost             ║  Low   ║  Med   ║  Med   ║  High      ║
║ Best for         ║Simple  ║Speed  ║Data   ║High-stakes ║
╚════════════════════╩═══════╩═══════╩═══════╩════════════╝
""".format(
        p1=results["p1"]["llm_calls"],
        p2=results["p2"]["llm_calls"],
        p3=results["p3"]["llm_calls"],
        p4=results["p4"]["llm_calls"],
    ))


if __name__ == "__main__":
    main()
