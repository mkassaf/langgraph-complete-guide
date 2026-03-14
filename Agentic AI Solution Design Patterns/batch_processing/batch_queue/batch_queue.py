"""
Batch Queue platform — distinct from Message Queue.

Consumer controls when and how many tasks to receive.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class BatchStatus(Enum):
    ACCUMULATING = "accumulating"
    READY = "ready"
    DISPATCHED = "dispatched"
    PROCESSED = "processed"


@dataclass
class BatchTask:
    """A single task waiting to be batched."""

    task_id: str = field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8]}")
    submitter_id: str = ""
    task_type: str = ""
    data: dict = field(default_factory=dict)
    submitted_at: str = field(
        default_factory=lambda: datetime.now().strftime("%H:%M:%S")
    )


@dataclass
class Batch:
    """
    A collection of tasks dispatched together.
    Consumer controls when and how many to receive.
    """

    batch_id: str = field(default_factory=lambda: f"BATCH-{uuid.uuid4().hex[:8]}")
    tasks: list[BatchTask] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%H:%M:%S")
    )
    dispatched_to: str = ""
    status: BatchStatus = BatchStatus.READY


class BatchQueue:
    """
    Batch Queue platform — distinct from Message Queue.

    From lesson: 'the consumer has more decision making
    power as to how and when it receives a batch. For
    example, even after establishing a polling connection,
    the consumer may only accept a batch when it contains
    a certain quantity of tasks.'

    Key: Consumer sets minimum batch size threshold.
    Queue waits until threshold is met before dispatching.
    """

    def __init__(self, queue_name: str):
        self.name = queue_name
        self._pending_tasks: list[BatchTask] = []
        self._batches: list[Batch] = []
        self._consumer_thresholds: dict[str, int] = {}
        self._processed_count: int = 0
        self.stats = {"submitted": 0, "batched": 0, "dispatched": 0}

    def submit_task(self, task: BatchTask, quiet: bool = False):
        """Producer submits a task. NON-BLOCKING."""
        self._pending_tasks.append(task)
        self.stats["submitted"] += 1
        if not quiet:
            print(
                f"[BATCH QUEUE:{self.name}] Task submitted by {task.submitter_id}\n"
                f"           Type: {task.task_type} | Pending: {len(self._pending_tasks)}\n"
                f"           Producer continues without waiting ✓"
            )

    def submit_bulk(self, tasks: list[BatchTask], submitter_id: str, quiet: bool = False):
        """Producer submits many tasks at once. Demonstrates bulk message exchange."""
        for t in tasks:
            t.submitter_id = submitter_id
            self._pending_tasks.append(t)
        self.stats["submitted"] += len(tasks)
        if not quiet:
            print(
                f"[BATCH QUEUE:{self.name}] BULK SUBMIT: {len(tasks)} tasks\n"
                f"           From: {submitter_id}\n"
                f"           Total pending: {len(self._pending_tasks)}"
            )
            print("           Producer continues without waiting ✓")

    def consumer_sets_threshold(self, consumer_id: str, min_batch_size: int):
        """Consumer declares minimum batch size it wants."""
        self._consumer_thresholds[consumer_id] = min_batch_size
        print(
            f"[BATCH QUEUE:{self.name}] {consumer_id} threshold set:\n"
            f"           Will only accept batches of {min_batch_size}+ tasks"
        )

    def poll_for_batch(self, consumer_id: str) -> Batch | None:
        """Consumer polls for a batch meeting their threshold."""
        threshold = self._consumer_thresholds.get(consumer_id, 1)
        pending = len(self._pending_tasks)
        print(
            f"[BATCH QUEUE:{self.name}] {consumer_id} polling...\n"
            f"           Pending tasks: {pending} | Required: {threshold}"
        )
        if pending >= threshold:
            batch_tasks = self._pending_tasks[:pending]
            del self._pending_tasks[:pending]
            batch = Batch(
                tasks=batch_tasks,
                dispatched_to=consumer_id,
                status=BatchStatus.DISPATCHED,
            )
            self._batches.append(batch)
            self.stats["batched"] += 1
            self.stats["dispatched"] += 1
            print(f"           → DISPATCHING batch of {len(batch_tasks)} tasks ✓")
            return batch
        print(f"           → Not enough tasks yet ({pending}/{threshold}) - waiting")
        return None

    def get_pending_count(self) -> int:
        """Tasks waiting to be batched."""
        return len(self._pending_tasks)

    def get_queue_stats(self) -> dict:
        """Full stats: submitted, batched, dispatched, processed."""
        return {
            **self.stats,
            "pending": self.get_pending_count(),
            "processed": self._processed_count,
        }

    def mark_batch_processed(self):
        """Mark that a batch was processed by consumer."""
        self._processed_count += 1
