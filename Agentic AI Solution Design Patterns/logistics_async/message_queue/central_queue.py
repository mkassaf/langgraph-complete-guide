"""
Central Message Queue — All 4 agents communicate through this.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class MessageCategory(Enum):
    NEW_ORDER = "new_order"
    OPTIMIZED_ROUTE = "optimized_route"
    VEHICLE_ASSIGNMENT = "vehicle_assignment"
    DISPATCH_CONFIRMATION = "dispatch_confirmation"
    FULFILLMENT_CONFIRMATION = "fulfillment_confirmation"


PRIORITY_ORDER = {"critical": 0, "express": 1, "standard": 2}


@dataclass
class LogisticsMessage:
    """
    Message flowing through the logistics async system.
    correlation_id stays the same for entire order lifecycle.
    """

    message_id: str = field(
        default_factory=lambda: f"MSG-{str(uuid.uuid4())[:6].upper()}"
    )
    correlation_id: str = ""
    category: MessageCategory = MessageCategory.NEW_ORDER
    sender_id: str = ""
    payload: dict = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%H:%M:%S")
    )
    priority: int = 1  # 0=critical, 1=express, 2=standard


class CentralMessageQueue:
    """
    The central message queue for the logistics system.
    All 4 agents communicate through this single queue.

    From lesson: 'sends this information in a message to
    a central message queue'
    """

    def __init__(self):
        self._queue: list[LogisticsMessage] = []
        self._message_log: list[dict] = []
        self.stats = {
            "total_sent": 0,
            "total_received": 0,
            "correlation_chains": {},
        }

    def send(self, message: LogisticsMessage):
        """Agent sends message to queue. NON-BLOCKING."""
        self._queue.append(message)
        self.stats["total_sent"] += 1
        order_id = message.payload.get("order", {}).get("order_id", "")
        if message.correlation_id:
            chain = self.stats["correlation_chains"].setdefault(
                message.correlation_id, []
            )
            chain.append(
                {
                    "category": message.category.value,
                    "sender": message.sender_id,
                    "order_id": order_id,
                }
            )
        self._message_log.append(
            {
                "msg_id": message.message_id,
                "corr_id": message.correlation_id,
                "category": message.category,
                "sender": message.sender_id,
            }
        )
        priority_tag = " ⚠️ CRITICAL PRIORITY" if message.payload.get("order", {}).get("priority") == "critical" else ""
        print(f"═══════════════════════════════════════")
        print(f"📨 [QUEUE] Message Received")
        print(f"   From:        {message.sender_id}")
        print(f"   Category:   {message.category.value}")
        print(f"   Correlation: {message.correlation_id}")
        print(f"   Order:      {order_id}{priority_tag}")
        print(f"═══════════════════════════════════════")

    def poll(
        self,
        consumer_id: str,
        category: MessageCategory,
    ) -> LogisticsMessage | None:
        """Agent polls for specific message category. Returns matching message or None."""
        print(f"[QUEUE] {consumer_id} polling for {category.value}...")
        # Sort by priority: critical first
        self._queue.sort(
            key=lambda m: (
                PRIORITY_ORDER.get(
                    m.payload.get("order", {}).get("priority", "standard"),
                    2,
                ),
                m.timestamp,
            )
        )
        for i, msg in enumerate(self._queue):
            if msg.category == category:
                self._queue.pop(i)
                self.stats["total_received"] += 1
                print(f"[QUEUE] → Delivering {msg.message_id} to {consumer_id}")
                return msg
        return None

    def get_queue_depth(self) -> int:
        """Messages currently waiting."""
        return len(self._queue)

    def get_correlation_chain(self, correlation_id: str) -> list[dict]:
        """Get all messages in an order's journey."""
        return self.stats["correlation_chains"].get(correlation_id, [])
