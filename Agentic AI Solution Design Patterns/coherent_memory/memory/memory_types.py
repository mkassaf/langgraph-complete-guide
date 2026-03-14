"""
Memory data structures for Coherent State and Collective Memory pattern.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class StateCategory(Enum):
    INVENTORY = "inventory"
    ORDER_STATUS = "order_status"
    AGENT_STATUS = "agent_status"
    TASK_PROGRESS = "task_progress"
    ENVIRONMENTAL = "environmental"
    SYSTEM_GOALS = "system_goals"
    EVENT_LOG = "event_log"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class StateEntry:
    """
    A single piece of state in the shared memory.
    Any agent can read or write these.
    """

    key: str
    value: dict | str | int | float
    category: StateCategory
    written_by: str
    timestamp: str
    version: int = 1


@dataclass
class AgentMemoryState:
    """
    Individual agent's private memory.
    Not visible to other agents directly.
    """

    agent_id: str
    current_objective: str
    recent_actions: list[str]
    observations: list[str]
    short_term: dict = field(default_factory=dict)
    long_term: dict = field(default_factory=dict)
    scratchpad: dict = field(default_factory=dict)


@dataclass
class SharedMemorySnapshot:
    """Complete snapshot of shared memory at a point in time."""

    timestamp: str
    entries: dict[str, "StateEntry"]
    total_entries: int
    last_updated_by: str
