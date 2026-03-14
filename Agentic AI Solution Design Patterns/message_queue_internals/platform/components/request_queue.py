"""
Request Queue — Component 1: Holds incoming request messages.
"""

from dataclasses import dataclass, field
from enum import Enum


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"


@dataclass
class Message:
    message_id: str
    correlation_id: str  # Links request ↔ response
    message_type: MessageType
    sender_id: str
    recipient_id: str
    payload: dict
    timestamp: str
    acknowledged: bool = False


class RequestQueue:
    """
    COMPONENT 1: Holds incoming request messages.

    From lesson: 'The message is sent to the message queue
    platform where it is first placed in a dedicated
    request queue component.'

    Messages wait here until dispatcher sends them.
    """

    def __init__(self):
        self._queue: list[Message] = []

    def enqueue(self, message: Message):
        """Add message to queue."""
        self._queue.append(message)
        print(f"[REQUEST QUEUE]    Message {message.message_id} enqueued")
        print(f"                   Correlation: {message.correlation_id} | From: {message.sender_id}")

    def peek(self) -> Message | None:
        """Look at next message without removing."""
        return self._queue[0] if self._queue else None

    def dequeue(self) -> Message | None:
        """Remove and return next message."""
        if not self._queue:
            return None
        msg = self._queue.pop(0)
        print(f"[REQUEST QUEUE]    Message {msg.message_id} dequeued for dispatch")
        return msg

    def size(self) -> int:
        """Messages waiting."""
        return len(self._queue)

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0
