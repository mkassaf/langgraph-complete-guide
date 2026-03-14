"""
Parent System Base Class

Abstract base for Central, Lightweight, and Hybrid parent systems.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from warehouse_architectures.environment import Task, TaskStatus, WarehouseEnvironment


class SystemArchitecture(Enum):
    """Type of agentic system architecture."""
    CENTRALIZED = "centralized"
    DECENTRALIZED = "decentralized"
    HYBRID = "hybrid"


@dataclass
class ConflictInfo:
    """Information about a resource conflict."""
    resource: str
    contenders: list[str]
    resolved: bool = False
    resolution: str = ""


class ParentSystem(ABC):
    """
    Base class for parent systems in agentic architectures.
    Implements Basic Agentic AI System Architectures concepts.
    """

    def __init__(self, env: WarehouseEnvironment):
        self.env = env
        self._tasks_completed: int = 0
        self._conflicts_resolved: int = 0
        self._failures_handled: int = 0

    @abstractmethod
    def assign_or_delegate_tasks(self, tasks: list[Task]) -> None:
        """Assign tasks to agents (centralized) or delegate goals (decentralized/hybrid)."""
        pass

    @abstractmethod
    def handle_conflict(self, conflict: dict[str, Any]) -> str:
        """Resolve resource conflict. Returns resolution description."""
        pass

    @abstractmethod
    def handle_agent_failure(self, agent_id: str) -> str:
        """Handle agent crash. Returns recovery description."""
        pass

    @abstractmethod
    def run_step(self) -> dict[str, Any]:
        """Execute one step. Returns step summary."""
        pass

    def get_progress(self) -> float:
        """System-wide completion percentage."""
        total = len(self.env.active_tasks)
        if total == 0:
            return 1.0
        completed = sum(1 for t in self.env.active_tasks if t.status == TaskStatus.COMPLETED)
        return completed / total
