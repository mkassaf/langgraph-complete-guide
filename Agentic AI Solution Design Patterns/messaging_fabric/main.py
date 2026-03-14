"""
Messaging Fabric Platforms — Entry Point

Demonstrates all three platforms in smart factory scenario.
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

from datetime import datetime

from llm_client import LLMClient
from fabric.messaging_fabric import MessagingFabric
from platforms.message_queue import QueueMessage, MessagePriority
from platforms.batch_queue import BatchItem
from agents.production_agent import ProductionAgent
from agents.quality_agent import QualityAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.safety_agent import SafetyAgent
from agents.report_agent import ReportAgent


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║       MESSAGING FABRIC PLATFORMS DEMONSTRATION      ║
║              Smart Factory Scenario                 ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()
    fabric = MessagingFabric()

    prod = ProductionAgent(llm)
    quality = QualityAgent(llm)
    maintenance = MaintenanceAgent(llm)
    safety = SafetyAgent(llm)
    report = ReportAgent(llm)

    # ========== PLATFORM 1: MESSAGE QUEUE ==========
    print("━" * 60)
    print("PLATFORM 1: MESSAGE QUEUE (Point-to-Point)")
    print("━" * 60)
    print("\n📋 3 production orders enqueued")

    for order in ProductionAgent.PRODUCTION_ORDERS:
        fabric.send_message(
            "production_orders",
            QueueMessage(
                message_id="",
                sender_id="scheduler",
                recipient_id="production_agent",
                content=order,
                priority=MessagePriority.HIGH,
                timestamp=datetime.now().isoformat(),
            ),
        )

    print("\n🏭 production_agent processing orders one by one:")
    for i in range(3):
        result = prod.process_next_order(fabric)
        if result:
            print(f"💭 LLM: Planning production of {result['order'].get('quantity', 0)} {result['order'].get('product', '')} units...")
            print(f"✅ {result['order'].get('order_id', '')} complete → sent to quality_checks queue")
        else:
            break

    print("\n📊 quality_agent processing quality checks:")
    for i in range(3):
        result = quality.process_quality_check(fabric)
        if result:
            print(f"💭 Quality check for {result['order'].get('order_id', '')} → submitted to batch")
        else:
            break

    # ========== PLATFORM 2: EVENT HUB ==========
    print("\n" + "━" * 60)
    print("PLATFORM 2: EVENT HUB (Publish-Subscribe)")
    print("━" * 60)
    print("\n📡 Subscriptions registered:")

    fabric.subscribe_to_events("maintenance_agent", ["overheat", "abnormal_vibration", "machine_failure"])
    fabric.subscribe_to_events("production_agent", ["overheat", "machine_failure", "line_stop", "production_started"])

    print("\n🔍 safety_agent monitoring sensors...")
    print("💭 LLM: Press-A temperature 95°C exceeds threshold 80°C!\n")

    safety.monitor_and_alert(fabric)

    print("\n🔧 maintenance_agent responding:")
    maint_results = maintenance.handle_safety_events(fabric)
    for r in maint_results:
        print(f"💭 LLM: {r['response'][:80]}...")
    print("ACTION: Schedule emergency maintenance, ETA 2 hours")

    print("\n🏭 production_agent responding:")
    print("💭 LLM: Press-A offline - rerouting to Press-B")

    # ========== PLATFORM 3: BATCH QUEUE ==========
    print("\n" + "━" * 60)
    print("PLATFORM 3: BATCH QUEUE (Aggregate Processing)")
    print("━" * 60)
    print("\n📊 Quality checks accumulated (3 items submitted earlier)\n")

    print("📋 report_agent processing batch:")
    report_result = report.generate_shift_report(fabric)
    if "report" in report_result:
        print("💭 LLM: Analyzing 3 quality checks together...\n")
        print("SHIFT REPORT:")
        for line in report_result["report"].split("\n")[:10]:
            print(f"  {line}")
    if "error" in report_result:
        print(f"  (No batch: {report_result['error']})")

    # ========== FABRIC STATS ==========
    stats = fabric.get_fabric_stats()
    print("\n" + "━" * 60)
    print("MESSAGING FABRIC STATISTICS")
    print("━" * 60)
    print("\nMESSAGE QUEUES:")
    for name, s in stats["message_queues"].items():
        print(f"  {name}: {s.get('total_logged', 0)} enqueued, {s.get('processed', 0)} processed")
    print("\nEVENT HUB:")
    eh = stats["event_hub"]
    print(f"  Events published: {eh.get('events_published', 0)}")
    print(f"  Total deliveries: {eh.get('total_deliveries', 0)}")
    print(f"  Event types: {eh.get('by_type', {})}")
    print("\nBATCH QUEUES:")
    for name, s in stats["batch_queues"].items():
        print(f"  {name}: {s.get('pending', 0)} pending, {s.get('completed', 0)} batches completed")

    total_msgs = (
        sum(s.get("total_logged", 0) for s in stats["message_queues"].values())
        + eh.get("total_deliveries", 0)
        + sum(s.get("completed", 0) for s in stats["batch_queues"].values()) * 3
    )
    print(f"\nTOTAL MESSAGES THROUGH FABRIC: ~{total_msgs}")
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║ KEY INSIGHT:                                        ║")
    print("║ Each platform serves a different communication     ║")
    print("║ pattern. Together they form the nervous system     ║")
    print("║ of the agentic AI factory.                         ║")
    print("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
