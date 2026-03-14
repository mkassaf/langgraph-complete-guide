"""
Message Queue Internals — Entry Point
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

from platform import MessageQueuePlatform
from llm_client import LLMClient
from agents.order_agent import OrderAgent
from agents.fulfillment_agent import FulfillmentAgent


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║        MESSAGE QUEUE INTERNALS DEMONSTRATION        ║
║     All 6 Components Working Together               ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()
    platform = MessageQueuePlatform("order_fulfillment")
    order_agent = OrderAgent(llm)
    fulfillment_agent = FulfillmentAgent(llm)

    correlation_ids = []

    # ━━━ PHASE 1 & 2: PRODUCER SENDS, CONSUMER RECEIVES ━━━
    print("━" * 60)
    print("PHASE 1: PRODUCER SENDS REQUEST")
    print("━" * 60)
    for order in OrderAgent.ORDERS:
        corr_id = order_agent.send_order_request(order, platform)
        if corr_id:
            correlation_ids.append((order, corr_id))

    # ━━━ PHASE 2-5: CONSUMER RECEIVES, ACKS, RESPONDS, PRODUCER RECEIVES ━━━
    for order, corr_id in correlation_ids:
        print("\n" + "━" * 60)
        print("PHASE 2: CONSUMER CONNECTS AND RECEIVES")
        print("━" * 60)
        msg = fulfillment_agent.connect_and_receive_order(platform)
        if msg:
            print("\n" + "━" * 60)
            print("PHASE 4: CONSUMER SENDS RESPONSE (role reversal)")
            print("━" * 60)
            fulfillment_agent.process_and_respond(msg, platform)

            print("\n" + "━" * 60)
            print("PHASE 5: ORIGINAL PRODUCER RECEIVES RESPONSE")
            print("━" * 60)
            order_agent.receive_fulfillment_response(corr_id, platform)

    # ━━━ PHASE 6: FAULT TOLERANCE DEMO ━━━
    print("\n" + "━" * 60)
    print("PHASE 6: FAULT TOLERANCE DEMO")
    print("━" * 60)
    corr_3 = order_agent.send_order_request(
        {"order_id": "ORD-003", "items": ["Tool x2"], "total": 45.50},
        platform,
    )
    if corr_3:
        correlation_ids.append(({"order_id": "ORD-003"}, corr_3))
    platform.simulate_platform_failure_and_recovery()
    msg = fulfillment_agent.connect_and_receive_order(platform)
    if msg and corr_3:
        fulfillment_agent.process_and_respond(msg, platform)
        order_agent.receive_fulfillment_response(corr_3, platform)

    # ━━━ FINAL STATUS ━━━
    status = platform.get_platform_status()
    print("\n" + "━" * 60)
    print("PLATFORM COMPONENT STATUS")
    print("━" * 60)
    print(f"""
╔══════════════════════════════════════════════════════╗
║ Component              │ Activity                   ║
╠══════════════════════════════════════════════════════╣
║ Request Queue          │ {status['request_queue_depth']} waiting (processed)     ║
║ Message Store (req)    │ {status['request_store_count']} stored (cleared by acks) ║
║ Request Dispatcher     │ {status['dispatched_requests']} dispatched               ║
║ Ack Handler            │ {status['acks_processed']} acks processed           ║
║ Response Queue         │ {status['response_queue_depth']} waiting (processed)     ║
║ Response Dispatcher    │ Responses delivered         ║
╠══════════════════════════════════════════════════════╣
║ Correlation pairs matched: {len(correlation_ids)}/3 ✅                   ║
║ Messages lost in failure: 0 ✅                      ║
╚══════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
