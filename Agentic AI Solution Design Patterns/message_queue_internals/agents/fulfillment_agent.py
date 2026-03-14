"""
Fulfillment Agent — CONSUMER then PRODUCER role.
"""

from platform import MessageQueuePlatform
from platform.components import Message
from prompts import FULFILLMENT_PROMPT


class FulfillmentAgent:
    """
    Demonstrates CONSUMER then PRODUCER role.

    1. Acts as CONSUMER: receives order request
    2. Acknowledges receipt
    3. Acts as PRODUCER: sends fulfillment response
    """

    agent_id = "fulfillment_agent"

    def __init__(self, llm_client):
        self.llm = llm_client

    def connect_and_receive_order(
        self,
        platform: MessageQueuePlatform,
    ) -> Message | None:
        """
        Connect to platform and poll for orders.
        When received, acknowledge immediately.
        """
        msg = platform.consumer_connect_and_receive(self.agent_id)
        if msg:
            print("\n" + "━" * 60)
            print("PHASE 3: CONSUMER ACKNOWLEDGES")
            print("━" * 60)
            platform.consumer_acknowledge(self.agent_id, msg)
        return msg

    def process_and_respond(
        self,
        received_message: Message,
        platform: MessageQueuePlatform,
    ):
        """
        LLM decides fulfillment details.
        Send response with same correlation_id.
        Now acting as producer.
        """
        order = received_message.payload.get("order", {})
        try:
            content = self.llm.generate(
                "You are a fulfillment agent (consumer role).",
                FULFILLMENT_PROMPT.format(order=order),
            )
        except Exception:
            content = "CARRIER: FedEx. TRACKING_ID: FDX-881293. STATUS: confirmed"
        print(f"💭 LLM: Processing order - {content[:60]}...")
        print(f"        Tracking: FDX-881293")
        print(f"\nConsumer now acting as PRODUCER for response:\n")
        platform.consumer_send_response(
            self.agent_id,
            received_message,
            {
                "original_order": order,
                "shipping": "FedEx express",
                "tracking": "FDX-881293",
                "estimated_days": 2,
                "status": "confirmed",
                "notes": content[:100],
            },
        )
