"""
Message Queue — Point-to-point sequential communication.
"""

from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import queue
import uuid


class MessagePriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class QueueMessage:
    """
    A message in the point-to-point queue.
    Processed one at a time, in order.
    Guaranteed delivery to ONE consumer.
    """

    message_id: str
    sender_id: str
    recipient_id: str
    content: dict
    priority: MessagePriority
    timestamp: str
    acknowledged: bool = False


class MessageQueue:
    """
    Point-to-point async communication.
    Each message processed exactly once.
    """

    def __init__(self, queue_name: str):
        self.name = queue_name
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._pending: list[tuple[int, QueueMessage]] = []
        self.message_log: list[QueueMessage] = []
        self.processed_count: int = 0

    def enqueue(self, message: QueueMessage):
        """Producer sends message to queue."""
        if not message.message_id:
            message.message_id = str(uuid.uuid4())[:8]
        if not message.timestamp:
            message.timestamp = datetime.now().isoformat()
        priority_val = 5 - message.priority.value  # Higher priority = lower number for PQ
        self._pending.append((priority_val, message))
        self._pending.sort(key=lambda x: (x[0], x[1].timestamp))
        self.message_log.append(message)
        print(f"[QUEUE:{self.name}] Message enqueued by {message.sender_id}")

    def dequeue(self, consumer_id: str) -> QueueMessage | None:
        """Consumer pulls next message from queue."""
        if not self._pending:
            return None
        _, message = self._pending.pop(0)
        message.acknowledged = True
        self.processed_count += 1
        print(f"[QUEUE:{self.name}] Message dequeued by {consumer_id}")
        return message

    def peek(self) -> QueueMessage | None:
        """Look at next message without consuming it."""
        if not self._pending:
            return None
        return self._pending[0][1]

    def size(self) -> int:
        """Number of messages waiting."""
        return len(self._pending)

    def get_stats(self) -> dict:
        """Queue statistics."""
        return {
            "total_logged": len(self.message_log),
            "processed": self.processed_count,
            "pending": self.size(),
        }
