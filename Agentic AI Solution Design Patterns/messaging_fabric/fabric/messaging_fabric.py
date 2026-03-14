"""
Messaging Fabric — Combines all three platforms.
"""

from datetime import datetime

from platforms.message_queue import MessageQueue, QueueMessage, MessagePriority
from platforms.event_hub import EventHub, Event
from platforms.batch_queue import BatchQueue, BatchItem


class MessagingFabric:
    """
    Combines all three platforms into unified fabric.
    Agents interact with the fabric, not individual platforms.
    """

    def __init__(self):
        self.message_queues: dict[str, MessageQueue] = {
            "production_orders": MessageQueue("production_orders"),
            "quality_checks": MessageQueue("quality_checks"),
        }
        self.event_hub = EventHub("factory_events")
        self.batch_queues: dict[str, BatchQueue] = {
            "quality_reports": BatchQueue("quality_reports", batch_size=3),
            "shift_summaries": BatchQueue("shift_summaries", batch_size=3),
        }

    def send_message(self, queue_name: str, message: QueueMessage):
        """Send via message queue (point-to-point)."""
        q = self.message_queues.get(queue_name)
        if q:
            q.enqueue(message)

    def receive_message(self, queue_name: str, consumer_id: str) -> QueueMessage | None:
        """Receive from message queue."""
        q = self.message_queues.get(queue_name)
        if q:
            return q.dequeue(consumer_id)
        return None

    def publish_event(self, event: Event) -> int:
        """Publish via event hub (broadcast)."""
        return self.event_hub.publish(event)

    def subscribe_to_events(self, subscriber_id: str, event_types: list[str]):
        """Subscribe to event types."""
        return self.event_hub.subscribe(subscriber_id, event_types)

    def get_pending_events(self, subscriber_id: str) -> list:
        """Get pending events for subscriber."""
        return self.event_hub.get_pending_events(subscriber_id)

    def consume_event(self, subscriber_id: str) -> Event | None:
        """Consume one event."""
        return self.event_hub.consume_event(subscriber_id)

    def submit_to_batch(self, queue_name: str, item: BatchItem):
        """Submit to batch queue (aggregate)."""
        bq = self.batch_queues.get(queue_name)
        if bq:
            return bq.submit(item)
        return None

    def trigger_batch(self, queue_name: str) -> object | None:
        """Manually trigger batch (or return last unprocessed batch if already triggered)."""
        bq = self.batch_queues.get(queue_name)
        if not bq:
            return None
        batch = bq.trigger_batch()
        if batch is None:
            batch = bq.get_last_unprocessed_batch()
        return batch

    def process_batch(self, queue_name: str, batch, processor_id: str):
        """Mark batch as processed by agent."""
        bq = self.batch_queues.get(queue_name)
        if bq:
            bq.process_batch(batch, processor_id)

    def get_fabric_stats(self) -> dict:
        """Stats across all three platforms."""
        queue_stats = {name: q.get_stats() for name, q in self.message_queues.items()}
        hub_stats = self.event_hub.get_delivery_stats()
        batch_stats = {
            name: {"pending": bq.get_pending_count(), "completed": len(bq.completed_batches)}
            for name, bq in self.batch_queues.items()
        }
        return {
            "message_queues": queue_stats,
            "event_hub": hub_stats,
            "batch_queues": batch_stats,
        }
