"""
Batch Queue platform — Consumer controls when and how many to receive.
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
    task_id: str = field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8]}")
    submitter_id: str = ""
    task_type: str = ""
    data: dict = field(default_factory=dict)
    submitted_at: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class Batch:
    batch_id: str = field(default_factory=lambda: f"BATCH-{uuid.uuid4().hex[:8]}")
    tasks: list[BatchTask] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    dispatched_to: str = ""
    status: BatchStatus = BatchStatus.READY


class BatchQueue:
    def __init__(self, queue_name: str):
        self.name = queue_name
        self._pending_tasks: list[BatchTask] = []
        self._batches: list[Batch] = []
        self._consumer_thresholds: dict[str, int] = {}
        self._processed_count: int = 0
        self.stats = {"submitted": 0, "batched": 0, "dispatched": 0}

    def submit_task(self, task: BatchTask, quiet: bool = False):
        self._pending_tasks.append(task)
        self.stats["submitted"] += 1
        if not quiet:
            print(f"[BATCH QUEUE:{self.name}] Task by {task.submitter_id} | Pending: {len(self._pending_tasks)} | Continues ✓")

    def submit_bulk(self, tasks: list[BatchTask], submitter_id: str, quiet: bool = False):
        for t in tasks:
            t.submitter_id = submitter_id
            self._pending_tasks.append(t)
        self.stats["submitted"] += len(tasks)
        if not quiet:
            print(f"[BATCH QUEUE:{self.name}] BULK: {len(tasks)} tasks from {submitter_id} | Pending: {len(self._pending_tasks)} | Continues ✓")

    def consumer_sets_threshold(self, consumer_id: str, min_batch_size: int):
        self._consumer_thresholds[consumer_id] = min_batch_size
        print(f"[BATCH QUEUE:{self.name}] {consumer_id} threshold: {min_batch_size}+ tasks")

    def poll_for_batch(self, consumer_id: str) -> Batch | None:
        threshold = self._consumer_thresholds.get(consumer_id, 1)
        pending = len(self._pending_tasks)
        print(f"[BATCH QUEUE:{self.name}] {consumer_id} polling | Pending: {pending} | Required: {threshold}")
        if pending >= threshold:
            batch_tasks = self._pending_tasks[:pending]
            del self._pending_tasks[:pending]
            batch = Batch(tasks=batch_tasks, dispatched_to=consumer_id, status=BatchStatus.DISPATCHED)
            self._batches.append(batch)
            self.stats["batched"] += 1
            self.stats["dispatched"] += 1
            print(f"           → DISPATCHING batch of {len(batch_tasks)} ✓")
            return batch
        print(f"           → Not enough ({pending}/{threshold}) - waiting")
        return None

    def get_pending_count(self) -> int:
        return len(self._pending_tasks)

    def mark_batch_processed(self):
        self._processed_count += 1
