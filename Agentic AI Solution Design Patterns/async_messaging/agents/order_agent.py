"""
Order Agent — PRODUCER: receives customer orders.
"""

import time
from datetime import datetime

from message_queue.queue_platform import MessageQueuePlatform
from message_queue.message import Message, MessageType
from prompts import ORDER_VALIDATION_PROMPT


class OrderAgent:
    """
    PRODUCER agent - receives customer orders.

    Key behavior: After sending order to queue,
    DOES NOT WAIT - immediately processes next order.
    This demonstrates 'Decoupled Producer Task Deferral'
    """

    agent_id = "order_agent"
    SAMPLE_ORDERS = [
        {"order_id": "ORD-001", "items": ["Widget x3"], "total": 89.99, "priority": "standard"},
        {"order_id": "ORD-002", "items": ["Gadget x1"], "total": 299.99, "priority": "express"},
        {"order_id": "ORD-003", "items": ["Tool x2"], "total": 45.50, "priority": "standard"},
        {"order_id": "ORD-004", "items": ["Device x1"], "total": 599.99, "priority": "express"},
        {"order_id": "ORD-005", "items": ["Kit x4"], "total": 124.00, "priority": "standard"},
    ]

    def __init__(self, llm_client):
        self.llm = llm_client

    def process_orders_async(
        self,
        platform: MessageQueuePlatform,
    ) -> list[str]:
        """
        Send all orders to queue WITHOUT waiting.
        LLM validates each order before sending.

        Show producer sending 5 orders rapidly
        while consumer hasn't started yet.
        This demonstrates LOAD LEVELING.
        """
        platform.create_queue("orders")
        sent_ids = []
        start = time.perf_counter()
        for order in self.SAMPLE_ORDERS:
            try:
                content = self.llm.generate(
                    "You are an order processing agent.",
                    ORDER_VALIDATION_PROMPT.format(order=order),
                )
            except Exception:
                content = "VALID: yes. ACTION: send_to_queue"
            if "send_to_queue" in content.lower() or "valid" in content.lower():
                priority = 3 if order.get("priority") == "express" else 2
                msg = Message(
                    message_type=MessageType.TASK,
                    sender_id=self.agent_id,
                    recipient_id="inventory_agent",
                    payload={"order": order, "validation": content[:100]},
                    priority=priority,
                )
                platform.send("orders", msg)
                sent_ids.append(msg.message_id)
        elapsed = time.perf_counter() - start
        depth = platform.get_queue_depth("orders")
        print(f"✅ All {len(sent_ids)} orders queued in {elapsed:.2f}s")
        print(f"   Queue depth: {depth} messages waiting")
        print(f"   order_agent already moved to next task")
        return sent_ids

    def process_orders_sync(self, llm_client) -> list[dict]:
        """
        COMPARISON: Process orders synchronously.
        Must wait for each to complete before next.
        Show the inefficiency clearly.
        """
        results = []
        for order in self.SAMPLE_ORDERS:
            # Simulate: validate (LLM) -> inventory check (blocked) -> payment (blocked)
            try:
                content = llm_client.generate(
                    "You are an order processing agent.",
                    ORDER_VALIDATION_PROMPT.format(order=order),
                )
            except Exception:
                content = "VALID: yes"
            time.sleep(0.4)  # Simulate inventory wait
            time.sleep(0.3)  # Simulate payment wait
            results.append({"order_id": order["order_id"], "status": "complete"})
        return results
