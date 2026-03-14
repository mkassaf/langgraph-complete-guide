"""
Event Receiver — COMPONENT 1: Accepts events from producers.
"""

from .channel_partition import StoredEvent, EventChannel


class EventReceiver:
    """
    COMPONENT 1: Accepts events from producers.

    From lesson: 'A producer... publishes an event when
    it notices a significant state change or action. The
    event details are sent directly to the event hub by
    the producer... it is accepted by an event receiver
    function of the broker node.'

    First point of contact for all incoming events.
    """

    def __init__(self):
        self.received_count: int = 0
        self.receive_log: list[dict] = []

    def accept(
        self,
        publisher_id: str,
        event_type: str,
        payload: dict,
    ) -> StoredEvent:
        """Accept incoming event from producer. Validate and prepare for storage."""
        channel = self.determine_channel(event_type)
        event = StoredEvent(
            event_type=event_type,
            channel=channel,
            publisher_id=publisher_id,
            payload=payload,
        )
        self.received_count += 1
        self.receive_log.append(
            {"event_type": event_type, "publisher": publisher_id}
        )
        print(f"[EVENT RECEIVER]    Event accepted")
        print(f"                     From: {publisher_id}")
        print(f"                     Type: {event_type}")
        print(f"                     → Routing to storage...")
        return event

    def determine_channel(self, event_type: str) -> EventChannel:
        """Route event to correct channel based on type."""
        if event_type.startswith("machine_"):
            return EventChannel.MACHINE_EVENTS
        if event_type.startswith("safety_") or "guard" in event_type:
            return EventChannel.SAFETY_EVENTS
        if event_type.startswith("quality_") or "defect" in event_type:
            return EventChannel.QUALITY_EVENTS
        return EventChannel.SYSTEM_EVENTS
