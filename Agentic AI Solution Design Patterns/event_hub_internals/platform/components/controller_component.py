"""
Controller Component — COMPONENT 3: Manages channel metadata.
"""

from dataclasses import dataclass, field

from .channel_partition import EventChannel


@dataclass
class ChannelMetadata:
    channel: EventChannel
    partition_count: int
    total_events: int
    active_publishers: list[str] = field(default_factory=list)
    active_subscribers: list[str] = field(default_factory=list)
    retention_hours: int = 168


class ControllerComponent:
    """
    COMPONENT 3: Manages channel metadata.

    From lesson: 'There is generally a controller component
    responsible for managing the metadata for these
    event channels'

    Tracks configuration and statistics for all channels.
    """

    def __init__(self):
        self.channel_metadata: dict[EventChannel, ChannelMetadata] = {}
        self._initialize_channels()

    def _initialize_channels(self):
        """Setup metadata for all channels."""
        for channel in EventChannel:
            self.channel_metadata[channel] = ChannelMetadata(
                channel=channel,
                partition_count=1,
                total_events=0,
            )

    def register_publisher(self, publisher_id: str, channel: EventChannel):
        """Record new publisher for a channel."""
        meta = self.channel_metadata[channel]
        if publisher_id not in meta.active_publishers:
            meta.active_publishers.append(publisher_id)
        print(f"[CONTROLLER]       Publisher {publisher_id} registered")
        print(f"                     for channel: {channel.value}")

    def register_subscriber(self, subscriber_id: str, channel: EventChannel):
        """Record new subscriber for a channel."""
        meta = self.channel_metadata[channel]
        if subscriber_id not in meta.active_subscribers:
            meta.active_subscribers.append(subscriber_id)
        print(f"[CONTROLLER]       Subscriber {subscriber_id} registered")
        print(f"                     for channel: {channel.value}")

    def update_event_count(self, channel: EventChannel):
        """Increment event count for channel."""
        self.channel_metadata[channel].total_events += 1
        print(f"[CONTROLLER]       Event count updated")
        print(f"                     {channel.value}: {self.channel_metadata[channel].total_events} total events")

    def get_channel_info(self, channel: EventChannel) -> ChannelMetadata:
        """Get current metadata for a channel."""
        return self.channel_metadata[channel]

    def print_all_metadata(self):
        """Print full metadata table for all channels."""
        for ch, meta in self.channel_metadata.items():
            if meta.total_events > 0 or meta.active_subscribers:
                print(f"  {ch.value}: {meta.total_events} events, "
                      f"publishers: {meta.active_publishers}, "
                      f"subscribers: {meta.active_subscribers}")
