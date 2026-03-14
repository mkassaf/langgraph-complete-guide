"""
Message bus for Planning pattern — routes work units between agents.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent
from datetime import datetime

from communication.work_unit import WorkUnit, WorkerType, WorkerResult


@dataclass
class Message:
    message_id: str
    sender_id: str
    recipient_id: str
    work_unit: WorkUnit
    timestamp: str


class MessageBus:
    """
    Routes work units between Orchestrator and Workers.

    This represents the communication layer in the
    Planning pattern's distributed architecture.
    """

    def __init__(self):
        self.workers: dict[WorkerType, "BaseAgent"] = {}
        self.message_log: list[Message] = []
        self._msg_counter = 0

    def register_worker(self, worker_type: WorkerType, worker: "BaseAgent"):
        """Register a worker agent."""
        self.workers[worker_type] = worker

    def send_to_worker(
        self,
        work_unit: WorkUnit,
        orchestrator_id: str,
    ) -> WorkerResult:
        """
        Route work unit to appropriate worker.
        Log the message.
        Return worker result.
        """
        worker = self.workers.get(work_unit.assigned_worker)
        if not worker:
            return WorkerResult(
                unit_id=work_unit.unit_id,
                worker_type=work_unit.assigned_worker,
                success=False,
                output={"error": "Worker not registered"},
                summary="Worker not found",
            )

        self._msg_counter += 1
        msg = Message(
            message_id=f"msg_{self._msg_counter}",
            sender_id=orchestrator_id,
            recipient_id=work_unit.assigned_worker.value,
            work_unit=work_unit,
            timestamp=datetime.now().isoformat(),
        )
        self.message_log.append(msg)

        result = worker.process(
            {
                "work_unit": work_unit,
                "orchestrator_id": orchestrator_id,
            }
        )

        return result

    def get_communication_log(self) -> list[Message]:
        """Full log of all orchestrator-worker messages."""
        return list(self.message_log)
