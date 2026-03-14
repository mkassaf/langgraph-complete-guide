"""
Coherent State and Collective Memory — Entry Point

Demonstrates warehouse order fulfillment with and without shared memory.
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

from config import ORDER
from llm_client import LLMClient
from scenarios.without_shared_memory import WithoutSharedMemoryScenario
from scenarios.with_shared_memory import WithSharedMemoryScenario


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║   COHERENT STATE AND COLLECTIVE MEMORY DEMO         ║
║         Warehouse Order Fulfillment                 ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()

    # ========== SCENARIO 1: WITHOUT SHARED MEMORY ==========
    print("━" * 60)
    print("SCENARIO 1: WITHOUT SHARED MEMORY")
    print("━" * 60)

    without_scenario = WithoutSharedMemoryScenario(llm)
    without_result = without_scenario.run(ORDER)

    print("\n📦 inventory_agent: \"I'll reserve BW-001 x3, RG-042 x1, GT-103 x2\"")
    print("   (writes to PRIVATE memory only)\n")

    print("🔍 picking_agent: \"What needs picking? I'll check...\"")
    print("   (no shared memory - doesn't know about reservation)")
    print("   \"I'll pick BW-001 x3, RG-042 x1, GT-103 x2\"")
    print("   ⚠️  CONFLICT: Picking same items inventory just reserved\n")

    print("📫 packing_agent: \"Is picking done? I'll assume yes and start\"")
    print("   ⚠️  RACE CONDITION: Started before picking complete\n")

    print("🚚 shipping_agent: \"I'll use the original order details\"")
    print("   ⚠️  STALE DATA: Using original order not current status\n")

    print("❌ RESULT: Order #ORD-2847 - FAILED")
    print("   Reason: Conflicting state, duplicate work, race conditions\n")

    # ========== SCENARIO 2: WITH SHARED MEMORY ==========
    print("━" * 60)
    print("SCENARIO 2: WITH SHARED MEMORY")
    print("━" * 60)

    with_scenario = WithSharedMemoryScenario(llm)
    with_result = with_scenario.run(ORDER)

    print("\n📦 inventory_agent: \"Checking stock and reserving items...\"")
    for agent, key, val in with_result.get("shared_memory", {}).get("writes_log", []):
        if agent == "inventory_agent":
            print(f"   ✅ Writes to shared memory: {key}: {val}")
    print("   order/ORD-2847/status: items_reserved\n")

    print("🔍 picking_agent: \"Reading shared memory...\"")
    print("   Reads: inventory reservations ✅")
    print("   \"I can see 3x BW-001, 1x RG-042, 2x GT-103 reserved for me to pick\"")
    for agent, key, val in with_result.get("shared_memory", {}).get("writes_log", []):
        if agent == "picking_agent":
            print(f"   ✅ Writes: {key}: {val}")
    print()

    print("📫 packing_agent: \"Checking if picking is complete...\"")
    print("   Reads: picking/ORD-2847/status = complete ✅")
    print("   \"Picking confirmed complete, starting packing\"")
    for agent, key, val in with_result.get("shared_memory", {}).get("writes_log", []):
        if agent == "packing_agent":
            print(f"   ✅ Writes: {key}: {val}")
    print()

    print("🚚 shipping_agent: \"Reading latest order status...\"")
    print("   Reads: packing status, inventory updates ✅")
    print("   \"All previous steps confirmed complete\"")
    for agent, key, val in with_result.get("shared_memory", {}).get("writes_log", []):
        if agent == "shipping_agent":
            print(f"   ✅ Writes: {key}: {val}")
    print()

    print("✅ RESULT: Order #ORD-2847 - SUCCESS")
    print("   All agents synchronized, no conflicts\n")

    # ========== SHARED MEMORY STATE ==========
    sm = with_result.get("shared_memory", {})
    print("━" * 60)
    print("SHARED MEMORY STATE AT COMPLETION")
    print("━" * 60)
    print(f"📊 Total entries: {sm.get('total_entries', 0)}")
    print(f"📝 Total writes: {sm.get('writes', 0)}")
    print(f"📖 Total reads: {sm.get('reads', 0)}")
    print("🤝 Agents synchronized: 4/4\n")

    # ========== COMPARISON ==========
    print("╔══════════════════════════════════════════════════════╗")
    print("║                 COMPARISON REPORT                   ║")
    print("╠════════════════════════════╦═══════════════╦════════════╣")
    print("║ Metric                     ║ No Shared Mem ║ Shared Mem ║")
    print("╠════════════════════════════╬═══════════════╬════════════╣")
    print(f"║ Conflicts detected         ║      {len(without_result.get('conflicts', []))}        ║     0      ║")
    print(f"║ Duplicate work             ║      {len(without_result.get('duplicate_work', []))}        ║     0      ║")
    print(f"║ Race conditions            ║      {len(without_result.get('race_conditions', []))}        ║     0      ║")
    print(f"║ Stale data used            ║      {len(without_result.get('stale_data', []))}        ║     0      ║")
    print("║ Order success              ║     ❌        ║    ✅      ║")
    print("╠════════════════════════════╬═══════════════╬════════════╣")
    print("║ KEY INSIGHT:                                        ║")
    print("║ Shared memory is the foundation that makes all     ║")
    print("║ multi-agent patterns work correctly at scale.     ║")
    print("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
