"""
Message data structures for async messaging architecture.
"""

from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    TASK = "task"


class MessageStatus(Enum):
    QUEUED = "queued"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"


@dataclass
class Message:
    """
    Core message unit in async messaging architecture.

    Key fields:
    - message_id: Unique identifier
    - correlation_id: Links request to response
      (both share same correlation_id)
    - sender_id / recipient_id: Agent identifiers
    """

    message_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    correlation_id: str = ""  # Links request ↔ response
    message_type: MessageType = MessageType.TASK
    sender_id: str = ""
    recipient_id: str = ""
    payload: dict = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%H:%M:%S")
    )
    status: MessageStatus = MessageStatus.QUEUED
    priority: int = 2  # 1=low, 2=medium, 3=high, 4=critical
    persist: bool = True  # Survives queue restart if True
    sequence_number: int = 0  # For FIFO ordering
