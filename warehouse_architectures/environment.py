"""
Shared Warehouse Environment

Provides warehouse map, tasks, agents, resource pool.
Supports conflict injection, agent failure, and unexpected events.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ResourceType(Enum):
    """Shared resources in the warehouse."""
    ELEVATOR = "elevator"
    STAIRS = "stairs"
    FORKLIFT = "forklift"
    PICKUP_ZONE = "pickup_zone"


@dataclass
class Task:
    """A single warehouse task."""
    task_id: str
    task_type: str  # "deliver_box" | "restock_shelf" | "customer_pickup"
    target: str  # room_id, shelf_id, or zone_id
    assigned_agent: str | None = None
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class ResourceState:
    """State of a shared resource."""
    resource_id: str
    resource_type: ResourceType
    in_use_by: str | None = None
    available: bool = True


class WarehouseEnvironment:
    """
    Shared warehouse environment for all three architectures.
    Implements conflict injection, agent failure, and unexpected events.
    """

    def __init__(self):
        self.warehouse_map: dict[str, Any] = {
            "rooms": ["301", "302", "303"],
            "shelves": ["A1", "A2", "B1", "B2"],
            "pickup_zones": ["P1", "P2"],
            "elevator": "E1",
            "stairs": "S1",
        }
        self.active_tasks: list[Task] = []
        self.active_agents: list[str] = []
        self.resource_pool: dict[str, ResourceState] = {
            "elevator": ResourceState("elevator", ResourceType.ELEVATOR),
            "stairs": ResourceState("stairs", ResourceType.STAIRS),
            "forklift": ResourceState("forklift", ResourceType.FORKLIFT),
        }
        self._failed_agents: set[str] = set()
        self._power_outage_section: str | None = None
        self._conflict_injected: bool = False

    def get_system_state(self) -> dict[str, Any]:
        """Full warehouse snapshot."""
        return {
            "tasks": [
                {
                    "id": t.task_id,
                    "type": t.task_type,
                    "target": t.target,
                    "assigned": t.assigned_agent,
                    "status": t.status.value,
                }
                for t in self.active_tasks
            ],
            "agents": list(self.active_agents),
            "failed_agents": list(self._failed_agents),
            "resources": {
                k: {
                    "in_use_by": v.in_use_by,
                    "available": v.available,
                }
                for k, v in self.resource_pool.items()
            },
            "power_outage": self._power_outage_section,
        }

    def inject_conflict(self, resource: str = "elevator") -> dict[str, Any]:
        """Two agents need same resource simultaneously."""
        self._conflict_injected = True
        return {
            "type": "resource_conflict",
            "resource": resource,
            "contenders": ["Robot_A", "Robot_C"],
        }

    def inject_agent_failure(self, agent_id: str) -> None:
        """Simulate agent crash."""
        self._failed_agents.add(agent_id)
        if agent_id in self.active_agents:
            self.active_agents.remove(agent_id)
        for t in self.active_tasks:
            if t.assigned_agent == agent_id:
                t.status = TaskStatus.FAILED

    def inject_unexpected_event(self, event: str = "power_outage_section_b") -> None:
        """E.g., power outage in section B."""
        self._power_outage_section = "B"

    def clear_unexpected_event(self) -> None:
        """Clear power outage."""
        self._power_outage_section = None

    def request_resource(self, agent_id: str, resource: str) -> tuple[bool, str]:
        """Agent requests resource. Returns (success, message)."""
        r = self.resource_pool.get(resource)
        if not r:
            return False, "Unknown resource"
        if r.in_use_by and r.in_use_by != agent_id:
            return False, f"Resource in use by {r.in_use_by}"
        r.in_use_by = agent_id
        r.available = False
        return True, f"{agent_id} acquired {resource}"

    def release_resource(self, agent_id: str, resource: str) -> None:
        """Agent releases resource."""
        r = self.resource_pool.get(resource)
        if r and r.in_use_by == agent_id:
            r.in_use_by = None
            r.available = True

    def is_section_accessible(self, section: str) -> bool:
        """Check if section has power."""
        if self._power_outage_section and section.upper().startswith(self._power_outage_section):
            return False
        return True

    def add_task(self, task: Task) -> None:
        self.active_tasks.append(task)

    def set_tasks(self, tasks: list[Task]) -> None:
        self.active_tasks = tasks

    def reset(self) -> None:
        """Reset for new scenario."""
        self._failed_agents.clear()
        self._power_outage_section = None
        self._conflict_injected = False
        for r in self.resource_pool.values():
            r.in_use_by = None
            r.available = True
