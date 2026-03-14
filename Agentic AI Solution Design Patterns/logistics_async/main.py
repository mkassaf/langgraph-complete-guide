"""
Logistics Async Messaging — Entry Point
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

from message_queue import CentralMessageQueue
from data.orders import CUSTOMER_ORDERS
from llm_client import LLMClient
from agents.new_order_agent import NewOrderAgent
from agents.route_optimization_agent import RouteOptimizationAgent
from agents.vehicle_assignment_agent import VehicleAssignmentAgent
from agents.dispatch_agent import DispatchAgent


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║    LOGISTICS ASYNC MESSAGING SCENARIO DEMO          ║
║      Fleet Management with 4 AI Agents              ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()
    queue = CentralMessageQueue()
    new_order = NewOrderAgent(llm, queue)
    route_opt = RouteOptimizationAgent(llm, queue)
    vehicle_assign = VehicleAssignmentAgent(llm, queue)
    dispatch = DispatchAgent(llm, queue)

    correlation_ids = []

    # ━━━ PHASE 1: NEW ORDERS RECEIVED (new_order_agent as PRODUCER) ━━━
    print("━" * 60)
    print("PHASE 1: NEW ORDERS RECEIVED (new_order_agent as PRODUCER)")
    print("━" * 60)
    print("\n📦 new_order_agent receiving 3 orders rapidly...\n")
    for order in CUSTOMER_ORDERS:
        corr_id = new_order.receive_and_dispatch_order(order)
        if corr_id:
            correlation_ids.append((corr_id, order))
    print(f"\nQueue depth: {queue.get_queue_depth()} messages")
    print("new_order_agent: Free to receive more orders ✓")

    # ━━━ PHASE 2: ROUTE OPTIMIZATION ━━━
    print("\n" + "━" * 60)
    print("PHASE 2: ROUTE OPTIMIZATION")
    print("━" * 60)
    print("\n🗺️  route_optimization_agent polling queue...")
    for _ in range(3):
        route_opt.poll_and_optimize()

    # ━━━ PHASE 3: VEHICLE ASSIGNMENT ━━━
    print("\n" + "━" * 60)
    print("PHASE 3: VEHICLE ASSIGNMENT")
    print("━" * 60)
    print("\n🚛 vehicle_assignment_agent polling queue...")
    for _ in range(3):
        vehicle_assign.poll_and_assign()

    # ━━━ PHASE 4: DISPATCH ━━━
    print("\n" + "━" * 60)
    print("PHASE 4: DISPATCH")
    print("━" * 60)
    print("\n📡 dispatch_agent polling queue...")
    for _ in range(3):
        dispatch.poll_and_dispatch()

    # ━━━ PHASE 5: ORDER COMPLETION (new_order_agent as CONSUMER) ━━━
    print("\n" + "━" * 60)
    print("PHASE 5: ORDER COMPLETION (new_order_agent as CONSUMER)")
    print("━" * 60)
    print("\n📦 new_order_agent polling for fulfillment confirmations...\n")
    new_order.poll_for_fulfillment()

    # ━━━ FINAL TRACKING TABLE ━━━
    print("\n" + "━" * 60)
    print("ORDER JOURNEY TRACKING")
    print("━" * 60)
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║           ORDER JOURNEY TRACKING                    ║")
    print("╠══════════════╦══════════════════════════════════════╣")
    print("║ Order        ║ Correlation Journey                  ║")
    print("╠══════════════╬══════════════════════════════════════╣")
    for corr_id, order in correlation_ids:
        chain = queue.get_correlation_chain(corr_id)
        stages = " → ".join(c.get("category", "")[:4] for c in chain) if chain else "NEW_ORDER → ROUTE → ASSIGN → DISPATCH → FULFILLED"
        order_id = order.get("order_id", "")
        customer = order.get("customer", "")
        tag = " ⚠️ CRITICAL" if order.get("priority") == "critical" else ""
        print(f"║ {order_id:<12} ║ {corr_id}:")
        print(f"║ ({customer[:10]:<10})  ║ {stages} ✅{tag}")
        print("╠══════════════╬══════════════════════════════════════╣")
    print(f"║ Total messages: {queue.stats['total_sent']} (5 per order)     ║")
    print(f"║ Correlation chains: {len(correlation_ids)}/{len(correlation_ids)} ✅                  ║")
    print(f"║ Orders fulfilled: {len(correlation_ids)}/{len(correlation_ids)} ✅                            ║")
    print("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
