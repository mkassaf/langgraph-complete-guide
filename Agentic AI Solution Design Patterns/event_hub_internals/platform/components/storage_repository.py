"""
Storage Repository — COMPONENT 2: Long-term event storage.
"""

from .channel_partition import ChannelPartition, EventChannel, StoredEvent


class StorageRepository:
    """
    COMPONENT 2: Long-term event storage.

    From lesson: 'unlike in message queues where messages
    are only held for as long as needed to complete the
    delivery requirements, event hubs store messages for
    longer periods.'

    Reasons for long-term storage:
    1. Many subscribers - all need chance to receive
    2. Logging requirements
    3. Event replay capability
    """

    def __init__(self):
        self.partitions: dict[EventChannel, list[ChannelPartition]] = {
            ch: [ChannelPartition(ch, 0)] for ch in EventChannel
        }
        self.total_stored: int = 0

    def store(self, event: StoredEvent) -> ChannelPartition:
        """Store event in appropriate channel partition."""
        part_list = self.partitions[event.channel]
        part = part_list[0]
        part.append(event)
        self.total_stored += 1
        print(f"[STORAGE REPO]      Stored in {event.channel.value}/partition-{part.partition_id}")
        print(f"                     Offset: {event.offset}")
        print(f"                     Note: Event persists for all subscribers + replay")
        return part

    def get_partition(
        self,
        channel: EventChannel,
        partition_id: int = 0,
    ) -> ChannelPartition:
        """Get specific partition for reading."""
        return self.partitions[channel][partition_id]

    def get_storage_stats(self) -> dict:
        """Stats per channel."""
        stats = {}
        for ch, parts in self.partitions.items():
            total = sum(p.get_size() for p in parts)
            if total > 0:
                events = parts[0]._events
                stats[ch.value] = {
                    "count": total,
                    "oldest": events[0].timestamp if events else "",
                    "newest": events[-1].timestamp if events else "",
                }
        return stats
