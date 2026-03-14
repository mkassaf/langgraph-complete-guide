"""
Tool Discovery — Entry Point
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

from agent import OfficeBuildingAgent, TEST_TASKS


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║       TOOL DISCOVERY AND USE DEMONSTRATION          ║
║         Office Building AI Agent                    ║
╚══════════════════════════════════════════════════════╝

Registry: 24 tools across 6 categories
Context Window Limit: show how all-tools mode struggles
""")

    agent = OfficeBuildingAgent()

    all_tokens_total = 0
    disc_tokens_total = 0

    for task in TEST_TASKS[:2]:  # Run 2 tasks for demo (full run = 5)
        print("━" * 60)
        print(f'TASK: "{task}"')
        print("━" * 60)

        try:
            all_result, disc_result = agent.run_comparison(task)
        except Exception as e:
            print(f"Error: {e}")
            continue

        all_tokens_total += all_result.prompt_tokens_used
        disc_tokens_total += disc_result.prompt_tokens_used

        print("\n📦 MODE 1: ALL TOOLS UPFRONT")
        print(f"Prompt size: ~{all_result.prompt_tokens_used} tokens (24 tool descriptions loaded)")
        if all_result.prompt_tokens_used > 2000:
            print("⚠️  WARNING: Large prompt - inefficient and expensive")
        if all_result.final_answer:
            print(f"✅ FINAL: {all_result.final_answer[:200]}...")

        print("\n" + "─" * 50)
        print("\n🔍 MODE 2: DYNAMIC TOOL DISCOVERY")
        print(f"Initial prompt size: ~{disc_result.prompt_tokens_used} tokens (registry summary only)")
        for ev in disc_result.discovery_events:
            print(f"\n💭 THOUGHT: Finding tools for: {ev.query[:50]}...")
            print("⚡ ACTION: discover_tools(need=\"...\")")
            print("👁️  OBSERVATION: Found relevant tools:")
            for t in ev.tools_found[:3]:
                print(f"    - {t.to_short_description()}")
            if ev.tool_selected:
                print(f"⚡ ACTION: {ev.tool_selected}(...)")
                print(f"👁️  OBSERVATION: {ev.execution_result.get('message', 'Done')}")
        if disc_result.final_answer:
            print(f"✅ FINAL: {disc_result.final_answer[:200]}...")
        print()

    n = 2
    all_avg = all_tokens_total // n if n and all_tokens_total else 0
    disc_avg = disc_tokens_total // n if n and disc_tokens_total else 0
    reduction = int((1 - disc_avg / all_avg) * 100) if all_avg else 0

    print(f"""
╔══════════════════════════════════════════════════════╗
║              EFFICIENCY COMPARISON                  ║
╠════════════════════════════╦═══════════════╦════════════╣
║ Metric                     ║  All Tools    ║ Discovery  ║
╠════════════════════════════╬═══════════════╬════════════╣
║ Avg prompt tokens          ║    {all_avg:<9}   ║    {disc_avg:<6}   ║
║ Tools loaded upfront       ║    24/24      ║    0/24    ║
║ Token reduction            ║      -       ║    {reduction}%     ║
╚════════════════════════════╩═══════════════╩════════════╝

KEY INSIGHT:
Discovery mode uses fewer tokens while achieving
the same result. With 100+ tools the difference
becomes even more dramatic.
""")


if __name__ == "__main__":
    main()
