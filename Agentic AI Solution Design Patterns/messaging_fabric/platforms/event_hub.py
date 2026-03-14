"""
Event Hub — Publish-subscribe broadcast communication.
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Event:
    """
    An event published to the hub.
    Delivered to ALL subscribers of the event type.
    """

    event_id: str
    event_type: str
    publisher_id: str
    payload: dict
    timestamp: str
    severity: str  # "info"|"warning"|"critical"


@dataclass
class Subscription:
    subscriber_id: str
    event_types: list[str]
    callback_queue: list = field(default_factory=list)


class EventHub:
    """
    Publish-Subscribe async communication.
    ONE publisher → MANY subscribers simultaneously.
    """

    def __init__(self, hub_name: str):
        self.name = hub_name
        self.subscriptions: dict[str, Subscription] = {}
        self.event_log: list[Event] = []
        self.delivery_log: list[dict] = []
        self._event_type_counts: dict[str, int] = {}

    def subscribe(self, subscriber_id: str, event_types: list[str]) -> Subscription:
        """Agent subscribes to specific event types."""
        sub = Subscription(subscriber_id=subscriber_id, event_types=event_types)
        self.subscriptions[subscriber_id] = sub
        print(f"[HUB:{self.name}] {subscriber_id} subscribed to {event_types}")
        return sub

    def publish(self, event: Event) -> int:
        """Agent publishes event. Hub delivers to ALL matching subscribers."""
        if not event.event_id:
            event.event_id = str(uuid.uuid4())[:8]
        if not event.timestamp:
            event.timestamp = datetime.now().isoformat()

        self.event_log.append(event)
        self._event_type_counts[event.event_type] = self._event_type_counts.get(event.event_type, 0) + 1

        notified = []
        for sub_id, sub in self.subscriptions.items():
            if event.event_type in sub.event_types:
                sub.callback_queue.append(event)
                self.delivery_log.append({"event_id": event.event_id, "subscriber": sub_id})
                notified.append(sub_id)

        print(f"[HUB:{self.name}] {event.publisher_id} published {event.event_type} (severity: {event.severity})")
        print(f"  → delivered to {len(notified)} subscribers: {notified}")
        return len(notified)

    def get_pending_events(self, subscriber_id: str) -> list[Event]:
        """Get unprocessed events for a subscriber."""
        sub = self.subscriptions.get(subscriber_id)
        if not sub:
            return []
        return list(sub.callback_queue)

    def consume_event(self, subscriber_id: str) -> Event | None:
        """Subscriber consumes one pending event."""
        sub = self.subscriptions.get(subscriber_id)
        if not sub or not sub.callback_queue:
            return None
        return sub.callback_queue.pop(0)

    def get_delivery_stats(self) -> dict:
        """Stats: events published, total deliveries, per-type counts."""
        return {
            "events_published": len(self.event_log),
            "total_deliveries": len(self.delivery_log),
            "by_type": dict(self._event_type_counts),
        }
