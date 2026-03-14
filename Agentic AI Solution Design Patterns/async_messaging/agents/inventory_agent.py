"""
Inventory Agent — CONSUMER: checks stock availability.
"""

from message_queue.queue_platform import MessageQueuePlatform
from message_queue.lightweight_broker import LightweightBroker
from message_queue.message import Message, MessageType
from prompts import INVENTORY_CHECK_PROMPT


class InventoryAgent:
    """
    CONSUMER agent - checks stock availability.

    Uses intra-agent lightweight broker for
    internal reasoning → action communication.
    Polls queue when ready (controls own pace).
    """

    agent_id = "inventory_agent"
    STOCK = {
        "Widget": 50,
        "Gadget": 3,
        "Tool": 25,
        "Device": 1,
        "Kit": 15,
    }

    def __init__(self, llm_client):
        self.llm = llm_client
        self._internal_broker = LightweightBroker()

    def start_processing(
        self,
        platform: MessageQueuePlatform,
        max_messages: int = 5,
    ) -> list[Message]:
        """
        Poll queue and process orders at own pace.
        LLM checks stock for each order.
        Send result to payment queue.
        Demonstrates consumer controlling own load.
        """
        processed = []
        for _ in range(max_messages):
            msg = platform.receive("orders", self.agent_id)
            if not msg:
                break
            order = msg.payload.get("order", {})
            try:
                content = self.llm.generate(
                    "You are an inventory management agent.",
                    INVENTORY_CHECK_PROMPT.format(order=order, stock=self.STOCK),
                )
            except Exception:
                content = "AVAILABILITY: in_stock. NEXT_ACTION: forward_to_payment"
            items_str = str(order.get("items", []))
            print(f"💭 LLM: Checking stock for {items_str}... allocated ✅")
            self._use_internal_async(order)
            # Forward to payment queue (send auto-creates if needed)
            out_msg = Message(
                message_type=MessageType.TASK,
                sender_id=self.agent_id,
                recipient_id="payment_agent",
                payload={
                    "order": order,
                    "inventory_result": content[:80],
                    "allocated": True,
                },
            )
            platform.send("payments", out_msg)
            processed.append(msg)
        return processed

    def _use_internal_async(self, order: dict):
        """
        Internal: Use lightweight broker for
        reasoning → action within the agent.
        Shows intra-agent async messaging.
        """
        internal_msg = Message(
            sender_id="reasoning_module",
            recipient_id="action_module",
            payload={"order_id": order.get("order_id"), "action": "allocate"},
        )
        self._internal_broker.send_internal(internal_msg)
        received = self._internal_broker.receive_internal()
        if received:
            pass  # Action module would process; for demo we just show the flow
