"""
Payment Agent — CONSUMER + PRODUCER: async request-response with correlation IDs.
"""

import uuid
from message_queue.queue_platform import MessageQueuePlatform
from message_queue.message import Message, MessageType
from prompts import PAYMENT_PROCESSING_PROMPT


class PaymentAgent:
    """
    CONSUMER + PRODUCER agent.
    Demonstrates ASYNC REQUEST-RESPONSE with correlation IDs.

    Sends payment auth request → gets correlated response.
    Does NOT block waiting for auth response.
    """

    agent_id = "payment_agent"

    def __init__(self, llm_client):
        self.llm = llm_client

    def process_payments(
        self,
        platform: MessageQueuePlatform,
        max_messages: int = 5,
    ) -> list[dict]:
        """
        For each order:
        1. Send payment auth REQUEST (with correlation_id)
        2. Continue processing other tasks (don't wait!)
        3. Later, receive RESPONSE matching correlation_id
        4. Show correlation_id links them together
        """
        results = []
        for _ in range(max_messages):
            msg = platform.receive("payments", self.agent_id)
            if not msg:
                break
            order = msg.payload.get("order", {})
            try:
                content = self.llm.generate(
                    "You are a payment processing agent.",
                    PAYMENT_PROCESSING_PROMPT.format(order=order, total=order.get("total", 0)),
                )
            except Exception:
                content = "DECISION: approve"
            corr_id = str(uuid.uuid4())[:8]
            msg.correlation_id = corr_id
            print(f"[REQUEST]  {self.agent_id} → Queue | Correlation:{corr_id}")
            print(f"           {self.agent_id} continues other work...")
            self._simulate_payment_gateway_response(platform, msg)
            response = platform.receive_response("payment_responses", corr_id, self.agent_id)
            if response:
                platform.send(
                    "fulfillment",
                    Message(
                        message_type=MessageType.TASK,
                        sender_id=self.agent_id,
                        recipient_id="fulfillment_agent",
                        payload={
                            "order": order,
                            "payment_status": "approved",
                            "correlation_id": corr_id,
                        },
                    ),
                )
                results.append({"order_id": order.get("order_id"), "correlation_id": corr_id})
        return results

    def _simulate_payment_gateway_response(
        self,
        platform: MessageQueuePlatform,
        request_message: Message,
    ):
        """
        Simulate payment gateway sending correlated response.
        Same correlation_id as the request.
        """
        platform.send_response(
            "payment_responses",
            request_message,
            {"status": "approved", "auth_code": "AUTH-123"},
            "gateway",
        )
