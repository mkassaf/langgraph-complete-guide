"""
Central Event Hub — messaging fabric platform.
"""

from dataclasses import dataclass, field
from datetime import datetime

from event_hub.event import CityEvent, EventType


@dataclass
class Subscription:
    """An agent's subscription to specific event types."""

    subscriber_id: str
    event_types: list[EventType]
    received_events: list = field(default_factory=list)


class EventHub:
    """
    Central Event Hub - messaging fabric platform.

    From lesson: 'The Event Hub basically acts as a central
    collection point that can ingest and then stream a
    continuous flow of events.'

    Key behaviors:
    1. Producer publishes → Hub stores and streams
    2. Consumers subscribe to event types
    3. Hub delivers to ALL matching subscribers
    4. Producer has NO knowledge of subscribers
    5. Stores events for replay capability
    """

    def __init__(self, hub_name: str):
        self.name = hub_name
        self._subscriptions: dict[str, Subscription] = {}
        self._event_stream: list[CityEvent] = []
        self._delivery_log: list[dict] = []
        self._event_type_counts: dict[str, int] = {}
        self._severity_counts: dict[str, int] = {}
        self._location_counts: dict[str, int] = {}

    def subscribe(self, subscriber_id: str, event_types: list[EventType]):
        """Agent subscribes to event types."""
        self._subscriptions[subscriber_id] = Subscription(
            subscriber_id=subscriber_id,
            event_types=event_types,
        )
        types_str = ", ".join(e.value for e in event_types[:5])
        if len(event_types) > 5:
            types_str += f"... (and {len(event_types) - 5} more)"
        print(f"[EVENT HUB:{self.name}] {subscriber_id} subscribed to:")
        print(f"  {types_str}")

    def publish(self, event: CityEvent) -> int:
        """
        Producer publishes event to hub.
        Delivers to ALL matching subscribers immediately.
        Producer does NOT know who receives it.
        """
        self._event_stream.append(event)
        self._event_type_counts[event.event_type.value] = (
            self._event_type_counts.get(event.event_type.value, 0) + 1
        )
        self._severity_counts[event.severity.value] = (
            self._severity_counts.get(event.severity.value, 0) + 1
        )
        self._location_counts[event.location] = (
            self._location_counts.get(event.location, 0) + 1
        )
        notified = []
        for sub_id, sub in self._subscriptions.items():
            if event.event_type in sub.event_types:
                sub.received_events.append(event)
                self._delivery_log.append(
                    {"event_id": event.event_id, "subscriber": sub_id}
                )
                notified.append(sub_id)
        severity_tag = " ⚠️ CRITICAL" if event.severity.value == "critical" else ""
        print(f"═══════════════════════════════════════")
        print(f"🔔 [EVENT HUB:{self.name}] Event Published")
        print(f"   Type:      {event.event_type.value}{severity_tag}")
        print(f"   Severity:  {event.severity.value}")
        print(f"   Publisher: {event.publisher_id} (no knowledge of subscribers)")
        print(f"   Location:  {event.location}")
        print(f"   → Delivered to {len(notified)} subscribers: {notified}")
        print(f"═══════════════════════════════════════")
        return len(notified)

    def get_events(
        self,
        subscriber_id: str,
        max_events: int = 10,
    ) -> list[CityEvent]:
        """
        Consumer polls for their pending events.
        Returns events subscriber hasn't processed yet.
        Clears them from pending after return.
        """
        print(f"[EVENT HUB] {subscriber_id} polling...")
        sub = self._subscriptions.get(subscriber_id)
        if not sub or not sub.received_events:
            return []
        events = sub.received_events[:max_events]
        sub.received_events = sub.received_events[max_events:]
        print(f"[EVENT HUB] → {len(events)} events delivered to {subscriber_id}")
        return events

    def replay_events(
        self,
        event_types: list[EventType] | None = None,
        from_time: str | None = None,
        requester_id: str = "",
    ) -> list[CityEvent]:
        """
        Replay historical events from the stream.
        """
        if event_types:
            events = [e for e in self._event_stream if e.event_type in event_types]
        else:
            events = list(self._event_stream)
        if from_time:
            events = [e for e in events if e.timestamp >= from_time]
        print(f"[EVENT HUB] REPLAY requested by {requester_id}")
        print(f"           Replaying {len(events)} events from history...")
        return events

    def get_stream_stats(self) -> dict:
        """Statistics on event stream."""
        return {
            "total_events": len(self._event_stream),
            "by_type": dict(self._event_type_counts),
            "by_severity": dict(self._severity_counts),
            "delivery_count": len(self._delivery_log),
            "top_locations": dict(
                sorted(
                    self._location_counts.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]
            ),
        }
