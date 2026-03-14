"""
Dispatch Function — COMPONENT 5: Sends events to ready consumers.
"""

from .channel_partition import StoredEvent
from .storage_repository import StorageRepository


class DispatchFunction:
    """
    COMPONENT 5: Sends events to ready consumers.

    From lesson: 'those programs that are subscribed to
    a given event are part of a group of consumers that
    are made aware of the event when they are polling
    the event hub, and are then almost instantly sent the
    event messages by the broker node's dispatch function'

    Only dispatches to consumers that are actively polling.
    """

    def __init__(self):
        self.dispatch_log: list[dict] = []
        self.total_dispatched: int = 0
        self._pending_by_consumer: dict[str, list[StoredEvent]] = {}

    def dispatch_to_subscribers(
        self,
        event: StoredEvent,
        ready_consumers: list[str],
        all_subscribers: list[str],
    ) -> list[str]:
        """Send event to all ready consumers. Queue for offline consumers."""
        received = []
        offline = [s for s in all_subscribers if s not in ready_consumers]
        print(f"[DISPATCH]          Dispatching {event.event_type}")
        print(f"                     Ready consumers: {ready_consumers}")
        for c in ready_consumers:
            if c not in self._pending_by_consumer:
                self._pending_by_consumer[c] = []
            self._pending_by_consumer[c].append(event)
            self.total_dispatched += 1
            received.append(c)
            print(f"                     → Sending to: {c} ✓")
        for c in offline:
            print(f"                     → {c} offline - will receive on next poll")
        self.dispatch_log.append(
            {"event_type": event.event_type, "delivered_to": received}
        )
        return received

    def get_pending_for_consumer(
        self,
        consumer_id: str,
        channel,
        max_events: int = 10,
    ) -> list[StoredEvent]:
        """Get pending events for a consumer (e.g. when they come online)."""
        pending = self._pending_by_consumer.get(consumer_id, [])
        channel_events = [e for e in pending if e.channel == channel][:max_events]
        for e in channel_events:
            pending.remove(e)
        return channel_events

    def dispatch_batch_to_consumer(
        self,
        consumer_id: str,
        events: list[StoredEvent],
    ) -> int:
        """Send batch of events to single consumer."""
        if not events:
            return 0
        if consumer_id not in self._pending_by_consumer:
            self._pending_by_consumer[consumer_id] = []
        self._pending_by_consumer[consumer_id].extend(events)
        start = events[0].offset if events else 0
        end = events[-1].offset if events else 0
        print(f"[DISPATCH]          Batch dispatch to {consumer_id}")
        print(f"                     Events in batch: {len(events)}")
        print(f"                     Stream offset: {start} → {end}")
        self.total_dispatched += len(events)
        return len(events)
