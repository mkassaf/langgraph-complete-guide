"""
Batch Queue — Aggregate processing communication.
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class BatchItem:
    """Single item waiting to be batched."""

    item_id: str
    submitter_id: str
    data: dict
    submitted_at: str


@dataclass
class Batch:
    """
    A collected group of items ready for processing.
    Processed together as one unit.
    """

    batch_id: str
    items: list[BatchItem]
    created_at: str
    processed: bool = False
    result: dict = field(default_factory=dict)


class BatchQueue:
    """
    Batch processing communication.
    Efficient for data more valuable in aggregate than individually.
    """

    def __init__(
        self,
        queue_name: str,
        batch_size: int = 10,
        batch_trigger: str = "size",
    ):
        self.name = queue_name
        self.batch_size = batch_size
        self.batch_trigger = batch_trigger
        self.pending_items: list[BatchItem] = []
        self.completed_batches: list[Batch] = []

    def submit(self, item: BatchItem):
        """Submit item to batch queue. Auto-triggers batch if size reached."""
        if not item.item_id:
            item.item_id = str(uuid.uuid4())[:8]
        if not item.submitted_at:
            item.submitted_at = datetime.now().isoformat()
        self.pending_items.append(item)
        n = len(self.pending_items)
        print(f"[BATCH:{self.name}] Item submitted by {item.submitter_id} ({n}/{self.batch_size} items pending)")
        if n >= self.batch_size:
            return self.trigger_batch()
        return None

    def trigger_batch(self) -> Batch | None:
        """Manually trigger batch processing."""
        if not self.pending_items:
            return None
        batch = Batch(
            batch_id=str(uuid.uuid4())[:8],
            items=list(self.pending_items),
            created_at=datetime.now().isoformat(),
        )
        self.pending_items.clear()
        self.completed_batches.append(batch)
        print(f"[BATCH:{self.name}] Batch triggered: {len(batch.items)} items collected")
        return batch

    def process_batch(self, batch: Batch, processor_id: str) -> Batch:
        """Mark batch as being processed by agent."""
        batch.processed = True
        return batch

    def get_pending_count(self) -> int:
        """Items waiting to be batched."""
        return len(self.pending_items)

    def get_last_unprocessed_batch(self) -> Batch | None:
        """Get most recent batch that hasn't been processed yet."""
        for batch in reversed(self.completed_batches):
            if not batch.processed:
                return batch
        return None
