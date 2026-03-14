"""
Group Coordinator — COMPONENT 4: Manages subscriber groups.
"""

from dataclasses import dataclass, field

from .channel_partition import EventChannel


@dataclass
class ConsumerGroup:
    group_id: str
    channel: EventChannel
    members: list[str] = field(default_factory=list)
    group_offset: int = 0


class GroupCoordinator:
    """
    COMPONENT 4: Manages groups of subscribers.

    From lesson: 'a group coordinator that manages the
    group of consumers that are subscribed to the events'

    Tracks which consumers are:
    - Currently active/polling
    - Part of which groups
    - At which offset in the stream
    """

    def __init__(self):
        self.groups: dict[tuple[str, EventChannel], ConsumerGroup] = {}
        self.consumer_to_group: dict[str, str] = {}
        self.consumer_to_channels: dict[str, list[EventChannel]] = {}
        self.polling_consumers: set[str] = set()

    def create_group(self, group_id: str, channel: EventChannel) -> ConsumerGroup:
        """Create a new consumer group for a channel."""
        key = (group_id, channel)
        if key in self.groups:
            return self.groups[key]
        group = ConsumerGroup(group_id=group_id, channel=channel)
        self.groups[key] = group
        print(f"[GROUP COORD]      Group {group_id} created for {channel.value}")
        return group

    def join_group(self, group_id: str, consumer_id: str, channel: EventChannel):
        """Consumer joins a group."""
        key = (group_id, channel)
        if key not in self.groups:
            self.create_group(group_id, channel)
        group = self.groups[key]
        if consumer_id not in group.members:
            group.members.append(consumer_id)
        self.consumer_to_group[consumer_id] = group_id
        print(f"[GROUP COORD]      {consumer_id} joined group: {group_id}")
        print(f"                     Group size: {len(group.members)} members")

    def consumer_starts_polling(self, consumer_id: str):
        """Consumer indicates it's ready to receive."""
        self.polling_consumers.add(consumer_id)
        print(f"[GROUP COORD]      {consumer_id} now polling ← ready!")

    def consumer_stops_polling(self, consumer_id: str):
        """Consumer goes offline."""
        self.polling_consumers.discard(consumer_id)

    def get_ready_consumers(self, channel: EventChannel) -> list[str]:
        """Get all consumers currently polling for a channel."""
        result = []
        for consumer_id, channels in self.consumer_to_channels.items():
            if channel in channels and consumer_id in self.polling_consumers:
                result.append(consumer_id)
        return result

    def get_group_members(self, channel: EventChannel) -> list[str]:
        """All subscribers for a channel (polling or not)."""
        result = []
        for consumer_id, channels in self.consumer_to_channels.items():
            if channel in channels:
                result.append(consumer_id)
        return result

    def register_consumer_channel(self, consumer_id: str, channels: list[EventChannel]):
        """Register consumer's channel subscriptions."""
        self.consumer_to_channels[consumer_id] = channels
