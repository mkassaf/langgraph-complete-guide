"""
Fulfillment Agent — Final CONSUMER: ships orders (FIFO).
"""

from message_queue.queue_platform import MessageQueuePlatform
from message_queue.message import Message
from prompts import FULFILLMENT_PROMPT


class FulfillmentAgent:
    """
    Final CONSUMER agent - ships orders.

    Demonstrates SEQUENTIAL PROCESSING (FIFO).
    Orders must be fulfilled in the order they were paid.
    Shows queue ordering rules.
    """

    agent_id = "fulfillment_agent"

    def __init__(self, llm_client):
        self.llm = llm_client

    def fulfill_in_order(
        self,
        platform: MessageQueuePlatform,
        max_messages: int = 10,
    ) -> list[dict]:
        """
        FIFO processing - first paid = first shipped.
        LLM determines shipping method per order.
        Show sequence numbers maintained correctly.
        """
        results = []
        seq = 0
        for _ in range(max_messages):
            msg = platform.receive("fulfillment", self.agent_id)
            if not msg:
                break
            seq += 1
            order = msg.payload.get("order", {})
            payment_status = msg.payload.get("payment_status", "approved")
            try:
                content = self.llm.generate(
                    "You are a fulfillment agent.",
                    FULFILLMENT_PROMPT.format(
                        sequence_number=seq,
                        order=order,
                        payment_status=payment_status,
                    ),
                )
            except Exception:
                carrier = "FedEx" if seq % 2 == 1 else "UPS"
                content = f"CARRIER: {carrier} TRACKING_ID: TRK-{seq:06d}"
            tracking = "TRK-" + str(seq).zfill(6) if "TRK-" not in content else content.split("TRK-")[-1][:6]
            if "FedEx" in content or "UPS" in content or "USPS" in content:
                carrier = "FedEx" if "FedEx" in content else "UPS" if "UPS" in content else "USPS"
            else:
                carrier = "FedEx"
            print(f"Sequence {seq}: {order.get('order_id', '')} → {carrier} TRK-{seq:06d} ✅")
            results.append({"sequence": seq, "order_id": order.get("order_id"), "tracking": f"TRK-{seq:06d}"})
        return results

    def demonstrate_fault_tolerance(
        self,
        platform: MessageQueuePlatform,
    ):
        """
        Simulate fulfillment agent crashing.
        Show messages remain in queue.
        Agent recovers and continues from where it left off.
        """
        print("💥 Simulating fulfillment_agent crash...")
        platform.simulate_failure_and_recovery("fulfillment")
        print("✅ fulfillment_agent restarts: continues from remaining messages")
