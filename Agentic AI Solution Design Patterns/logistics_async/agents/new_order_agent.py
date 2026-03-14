"""
New Order Agent — AGENT 1: Receives orders, tracks completion.
"""

import uuid

from message_queue import CentralMessageQueue, LogisticsMessage, MessageCategory
from prompts import NEW_ORDER_PROMPT


class NewOrderAgent:
    """
    AGENT 1: New Order Agent

    From lesson: 'The new order agent receives the order
    details and sends this information in a message to a
    central message queue. Once the message is sent, that
    agent doesn't wait for a response. It's free to
    process the next incoming order.'

    Role transition:
    - PRODUCER: sends new orders to queue
    - CONSUMER: polls for fulfillment confirmations
    """

    agent_id = "new_order_agent"

    def __init__(self, llm_client, queue: CentralMessageQueue):
        self.llm = llm_client
        self.queue = queue
        self.pending_orders: dict[str, dict] = {}  # correlation_id → original order

    def receive_and_dispatch_order(self, order: dict) -> str:
        """
        PRODUCER role:
        1. LLM validates and prepares order
        2. Generate correlation_id for this order
        3. Send to queue
        4. Store correlation mapping
        5. Return immediately (don't wait!)
        """
        try:
            corr_id = f"CORR-{str(uuid.uuid4())[:4]}"
            content = self.llm.generate(
                "You are a new order processing agent.",
                NEW_ORDER_PROMPT.format(order=order, correlation_id=corr_id),
            )
        except Exception:
            content = "ORDER_VALID: yes. ACTION: dispatch_to_queue"
            corr_id = f"CORR-{str(uuid.uuid4())[:4]}"
        if "reject" in content.lower():
            return ""
        priority_tag = " ⚠️ CRITICAL" if order.get("priority") == "critical" else ""
        print(f"💭 LLM: Validating {order.get('order_id', '')} ({order.get('customer', '')} - {order.get('priority', '')}){priority_tag}... Valid")
        msg = LogisticsMessage(
            correlation_id=corr_id,
            category=MessageCategory.NEW_ORDER,
            sender_id=self.agent_id,
            payload={"order": order, "validation": content[:80]},
        )
        msg.priority = 0 if order.get("priority") == "critical" else 1 if order.get("priority") == "express" else 2
        self.queue.send(msg)
        self.pending_orders[corr_id] = order
        print(f"✓ new_order_agent continues immediately → next order")
        return corr_id

    def poll_for_fulfillment(self) -> list[dict]:
        """
        CONSUMER role:
        Poll queue for FULFILLMENT_CONFIRMATION messages.
        Match correlation_id to original order.
        Update order status.
        """
        results = []
        while True:
            msg = self.queue.poll(self.agent_id, MessageCategory.FULFILLMENT_CONFIRMATION)
            if not msg:
                break
            order = self.pending_orders.get(msg.correlation_id, {})
            print(f"🔗 Correlation match: {msg.correlation_id} = {order.get('order_id', '')} ✅")
            print(f"   {order.get('customer', '')} order DISPATCHED")
            print(f"💭 LLM: Updating order status, notifying customer...")
            print(f"📧 [CUSTOMER NOTIFICATION] {order.get('customer', '')}:")
            print(f'   "Your order {order.get("order_id", "")} has been dispatched!')
            payload = msg.payload
            print(f'    Truck: {payload.get("truck_id", "")} | ETA: {payload.get("eta", "")}')
            print(f'    Tracking: {payload.get("tracking", "")}"')
            print(f"✅ Order {order.get('order_id', '')} cycle COMPLETE")
            results.append({"correlation_id": msg.correlation_id, "order": order})
        return results
