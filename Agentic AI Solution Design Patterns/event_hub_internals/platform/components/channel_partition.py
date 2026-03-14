"""
Channel Partition — Event channel partitions with long-term retention.
"""

from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class EventChannel(Enum):
    MACHINE_EVENTS = "machine_events"
    SAFETY_EVENTS = "safety_events"
    QUALITY_EVENTS = "quality_events"
    SYSTEM_EVENTS = "system_events"


@dataclass
class StoredEvent:
    """
    Event stored in a channel partition.

    Key difference from Message Queue:
    NOT deleted after delivery.
    Kept for multiple subscribers + replay.
    """

    event_id: str = field(default_factory=lambda: f"EVT-{str(uuid.uuid4())[:6].upper()}")
    event_type: str = ""
    channel: EventChannel = EventChannel.MACHINE_EVENTS
    publisher_id: str = ""
    payload: dict = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%H:%M:%S")
    )
    delivered_to: list[str] = field(default_factory=list)
    offset: int = 0


class ChannelPartition:
    """
    A partition within an event channel.

    From lesson: 'routes the event to the broker's internal
    event storage repository where it is placed into a
    specific event channel partition'

    Unlike message queues: events persist long-term
    for multiple subscribers and replay purposes.
    """

    def __init__(self, channel: EventChannel, partition_id: int):
        self.channel = channel
        self.partition_id = partition_id
        self._events: list[StoredEvent] = []
        self._consumer_offsets: dict[str, int] = {}
        self._next_offset = 0

    def append(self, event: StoredEvent):
        """Add event to partition. Events NEVER automatically deleted."""
        event.offset = self._next_offset
        self._next_offset += 1
        self._events.append(event)
        print(f"[PARTITION:{self.channel.value}/{self.partition_id}] Event appended")
        print(f"           Total stored: {len(self._events)} (long-term retention)")

    def read_from_offset(
        self,
        consumer_id: str,
        max_events: int = 10,
    ) -> list[StoredEvent]:
        """Consumer reads events from their last position."""
        offset = self._consumer_offsets.get(consumer_id, 0)
        result = []
        for e in self._events:
            if e.offset >= offset and len(result) < max_events:
                result.append(e)
        if result:
            self._consumer_offsets[consumer_id] = result[-1].offset + 1
        return result

    def get_all_for_replay(self, from_offset: int = 0) -> list[StoredEvent]:
        """Return all events from a position for replay."""
        return [e for e in self._events if e.offset >= from_offset]

    def get_size(self) -> int:
        """Total events ever stored (not deleted)."""
        return len(self._events)
