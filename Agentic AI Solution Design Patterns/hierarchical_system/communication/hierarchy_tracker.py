"""
Hierarchy tracker — monitors system-wide state across all layers.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SystemSnapshot:
    """Current state of entire multi-agent system."""

    timestamp: str
    layer1_status: dict
    layer2_statuses: dict
    layer3_statuses: dict
    overall_progress: float
    active_agents: list[str]
    completed_tasks: list[str]
    failed_tasks: list[str]


class HierarchyTracker:
    """
    Monitors system-wide state across all layers.
    """

    def __init__(self):
        self._agent_status: dict[str, tuple[int, str, float]] = {}  # id -> (layer, status, progress)
        self._completed_tasks: list[str] = []
        self._failed_tasks: list[str] = []

    def update_agent_status(
        self,
        agent_id: str,
        layer: int,
        status: str,
        progress: float,
    ):
        """Update status of any agent in hierarchy."""
        self._agent_status[agent_id] = (layer, status, progress)

    def mark_completed(self, task_id: str):
        """Mark a task as completed."""
        if task_id not in self._completed_tasks:
            self._completed_tasks.append(task_id)

    def mark_failed(self, task_id: str):
        """Mark a task as failed."""
        if task_id not in self._failed_tasks:
            self._failed_tasks.append(task_id)

    def get_snapshot(self) -> SystemSnapshot:
        """Get current state of entire system."""
        l1 = {k: {"status": v[1], "progress": v[2]} for k, v in self._agent_status.items() if v[0] == 1}
        l2 = {k: {"status": v[1], "progress": v[2]} for k, v in self._agent_status.items() if v[0] == 2}
        l3 = {k: {"status": v[1], "progress": v[2]} for k, v in self._agent_status.items() if v[0] == 3}
        return SystemSnapshot(
            timestamp=datetime.now().isoformat(),
            layer1_status=l1,
            layer2_statuses=l2,
            layer3_statuses=l3,
            overall_progress=self.calculate_overall_progress(),
            active_agents=[k for k, v in self._agent_status.items() if v[1] == "in_progress"],
            completed_tasks=list(self._completed_tasks),
            failed_tasks=list(self._failed_tasks),
        )

    def calculate_overall_progress(self) -> float:
        """Aggregate progress across all agents."""
        if not self._agent_status:
            return 0.0
        return sum(v[2] for v in self._agent_status.values()) / len(self._agent_status)
