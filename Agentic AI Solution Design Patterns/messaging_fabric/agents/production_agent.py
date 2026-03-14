"""
Production Agent — uses Message Queue, publishes events.
"""

from datetime import datetime

from fabric.messaging_fabric import MessagingFabric
from platforms.message_queue import QueueMessage, MessagePriority
from platforms.event_hub import Event
from prompts import PRODUCTION_PROMPT


class ProductionAgent:
    """
    Manages production line operations.
    Uses: Message Queue (receives production orders)
    Publishes: Events (production milestones)
    """

    agent_id = "production_agent"
    PRODUCTION_ORDERS = [
        {"order_id": "ORD-001", "product": "Widget A", "quantity": 100},
        {"order_id": "ORD-002", "product": "Widget B", "quantity": 50},
        {"order_id": "ORD-003", "product": "Gadget X", "quantity": 75},
    ]

    def __init__(self, llm_client):
        self.llm = llm_client

    def process_next_order(self, fabric: MessagingFabric) -> dict | None:
        """Pull next order from queue. LLM plans. Publish event. Send to quality."""
        msg = fabric.receive_message("production_orders", self.agent_id)
        if not msg:
            return None
        order = msg.content
        try:
            content = self.llm.generate(
                "You are a production agent.",
                PRODUCTION_PROMPT.format(order=str(order), factory_status="Normal"),
            )
        except Exception:
            content = "PRODUCTION_PLAN: Standard assembly. ESTIMATED_TIME: 2 hours."

        fabric.publish_event(
            Event(
                event_id="",
                event_type="production_started",
                publisher_id=self.agent_id,
                payload={"order": order, "plan": content[:100]},
                timestamp=datetime.now().isoformat(),
                severity="info",
            )
        )

        fabric.send_message(
            "quality_checks",
            QueueMessage(
                message_id="",
                sender_id=self.agent_id,
                recipient_id="quality_agent",
                content={"order": order, "checks_needed": ["visual", "dimension"]},
                priority=MessagePriority.MEDIUM,
                timestamp=datetime.now().isoformat(),
            ),
        )
        return {"order": order, "plan": content[:200]}
