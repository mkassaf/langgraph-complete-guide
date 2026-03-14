"""
Event Hub Platform — Orchestrates all components.
"""

from .components import (
    EventChannel,
    StoredEvent,
    EventReceiver,
    StorageRepository,
    ControllerComponent,
    GroupCoordinator,
    DispatchFunction,
)


class BrokerNode:
    """
    The primary component of the Event Hub.
    Contains and orchestrates all internal components.

    From lesson: 'A typical event hub will usually rely on
    a broker node as its primary component, which also
    contains its primary operational logic.'
    """

    def __init__(self):
        self.event_receiver = EventReceiver()
        self.storage = StorageRepository()
        self.dispatch = DispatchFunction()


class EventHubPlatform:
    """
    Full Event Hub Platform - orchestrates all components.

    Internal flow:
    1. EventReceiver accepts event
    2. StorageRepository stores in ChannelPartition
    3. ControllerComponent updates metadata
    4. GroupCoordinator identifies ready subscribers
    5. DispatchFunction sends to ready consumers
    """

    def __init__(self, hub_name: str):
        self.name = hub_name
        self.broker = BrokerNode()
        self.controller = ControllerComponent()
        self.group_coordinator = GroupCoordinator()

    def register_publisher(self, publisher_id: str, channels: list[EventChannel]):
        """Register producer with controller."""
        for ch in channels:
            self.controller.register_publisher(publisher_id, ch)

    def subscribe(
        self,
        subscriber_id: str,
        channels: list[EventChannel],
        group_id: str | None = None,
    ):
        """Subscribe agent to channels. Registers with controller."""
        self.group_coordinator.register_consumer_channel(subscriber_id, channels)
        for ch in channels:
            self.controller.register_subscriber(subscriber_id, ch)
        if group_id:
            for ch in channels:
                self.group_coordinator.create_group(group_id, ch)
                self.group_coordinator.join_group(group_id, subscriber_id, ch)

    def publish(
        self,
        publisher_id: str,
        event_type: str,
        payload: dict,
    ) -> StoredEvent:
        """Full publish flow through all components."""
        print(f"\n╔══════════════════════════════════════╗")
        print(f"║   EVENT HUB: Full Publish Flow       ║")
        print(f"╚══════════════════════════════════════╝\n")
        print("1. ", end="")
        event = self.broker.event_receiver.accept(
            publisher_id, event_type, payload
        )
        print("\n2. ", end="")
        self.broker.storage.store(event)
        print("\n3. ", end="")
        self.controller.update_event_count(event.channel)
        ready = self.group_coordinator.get_ready_consumers(event.channel)
        all_subs = self.group_coordinator.get_group_members(event.channel)
        print("\n4. [GROUP COORD]      ", end="")
        if ready:
            for c in ready:
                print(f"{c} now polling ← ready! ", end="")
        if [s for s in all_subs if s not in ready]:
            for s in all_subs:
                if s not in ready:
                    print(f"{s}: offline (will get on next poll) ", end="")
        print("\n\n5. ", end="")
        self.broker.dispatch.dispatch_to_subscribers(
            event, ready, all_subs
        )
        return event

    def consumer_poll(
        self,
        consumer_id: str,
        channel: EventChannel,
    ) -> list[StoredEvent]:
        """Consumer polls for events. Returns unread events from partition."""
        self.group_coordinator.consumer_starts_polling(consumer_id)
        part = self.broker.storage.get_partition(channel)
        events = part.read_from_offset(consumer_id, max_events=10)
        if events:
            self.broker.dispatch.dispatch_log.append(
                {"consumer": consumer_id, "events": len(events)}
            )
        return events

    def consumer_starts_polling(self, consumer_id: str):
        """Mark consumer as ready to receive."""
        self.group_coordinator.consumer_starts_polling(consumer_id)

    def request_batch_stream(
        self,
        consumer_id: str,
        channel: EventChannel,
        batch_size: int = 5,
    ) -> list[StoredEvent]:
        """Consumer requests batch from stream."""
        part = self.broker.storage.get_partition(channel)
        events = part.read_from_offset(consumer_id, max_events=batch_size)
        if events:
            self.broker.dispatch.dispatch_batch_to_consumer(
                consumer_id, events
            )
        return events

    def replay_from_offset(
        self,
        requester_id: str,
        channel: EventChannel,
        from_offset: int = 0,
    ) -> list[StoredEvent]:
        """Request historical event replay."""
        part = self.broker.storage.get_partition(channel)
        events = part.get_all_for_replay(from_offset)
        print(f"[STORAGE REPO]      REPLAY requested by {requester_id}")
        print(f"                     Returning all {len(events)} events from offset {from_offset}")
        print(f"                     (Events never deleted - long-term retention)")
        return events

    def print_platform_status(self):
        """Full status of all components."""
        stats = self.broker.storage.get_storage_stats()
        total = self.broker.storage.total_stored
        ch_summary = ", ".join(f"{k}:{v['count']}" for k, v in stats.items()) if stats else "0"
        print(f"\n╔══════════════════════════════════════════════════╗")
        print(f"║         EVENT HUB COMPONENT STATUS              ║")
        print(f"╠══════════════════════════════════════════════════╣")
        print(f"║ Event Receiver     │ {self.broker.event_receiver.received_count} events accepted              ║")
        print(f"║ Storage Repository │ {total} stored (NEVER deleted)       ║")
        print(f"║ Channel Partitions │ {ch_summary} ║")
        print(f"║ Controller         │ {len(stats)} channels active              ║")
        print(f"║ Dispatch Function  │ {self.broker.dispatch.total_dispatched} deliveries made             ║")
        print(f"╠══════════════════════════════════════════════════╣")
        print(f"║ KEY DIFFERENCE FROM MESSAGE QUEUE:               ║")
        print(f"║ All events still in storage after delivery ✓   ║")
        print(f"║ Available for replay anytime ✓                  ║")
        print(f"╚══════════════════════════════════════════════════╝")
