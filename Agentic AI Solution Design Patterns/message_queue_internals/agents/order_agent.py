"""
Order Agent — PRODUCER then CONSUMER role.
"""

from platform import MessageQueuePlatform
from prompts import ORDER_VALIDATION_PROMPT, RESPONSE_PROCESSING_PROMPT


class OrderAgent:
    """
    Demonstrates PRODUCER then CONSUMER role.

    1. Acts as PRODUCER: sends order request
    2. Acts as CONSUMER: receives fulfillment response
    """

    agent_id = "order_agent"
    ORDERS = [
        {"order_id": "ORD-001", "items": ["Widget x3"], "total": 89.99},
        {"order_id": "ORD-002", "items": ["Gadget x1"], "total": 299.99},
    ]

    def __init__(self, llm_client):
        self.llm = llm_client

    def send_order_request(
        self,
        order: dict,
        platform: MessageQueuePlatform,
    ) -> str:
        """
        LLM validates order.
        Send to platform as producer.
        Return correlation_id.
        Does NOT wait for response.
        """
        try:
            content = self.llm.generate(
                "You are an order processing agent (producer).",
                ORDER_VALIDATION_PROMPT.format(order=order),
            )
        except Exception:
            content = "VALID: yes. DECISION: dispatch"
        if "reject" in content.lower():
            return ""
        print(f"💭 LLM: Validating order {order.get('order_id', '')}... Valid, dispatching")
        print(f"\n📤 order_agent (PRODUCER) sending request:\n")
        return platform.producer_send_request(
            sender_id=self.agent_id,
            recipient_id="fulfillment_agent",
            payload={"order": order, "validation": content[:80]},
            expects_response=True,
        )

    def receive_fulfillment_response(
        self,
        correlation_id: str,
        platform: MessageQueuePlatform,
    ) -> dict:
        """
        Later: receive correlated response.
        LLM processes fulfillment confirmation.
        """
        response = platform.producer_receive_response(self.agent_id, correlation_id)
        if not response:
            return {}
        try:
            content = self.llm.generate(
                "You are an order agent receiving fulfillment confirmation.",
                RESPONSE_PROCESSING_PROMPT.format(
                    correlation_id=correlation_id,
                    original_order=response.payload.get("original_order", {}),
                    response=response.payload,
                ),
            )
        except Exception:
            content = "ORDER_STATUS: fulfilled. CUSTOMER_NOTIFICATION: Order shipped."
        print(f"💭 LLM: Order confirmed! {content[:80]}...")
        print(f"        Notifying customer...")
        return {"response": response.payload, "processing": content}
