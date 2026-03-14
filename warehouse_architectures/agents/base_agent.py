"""
Base Agent — Abstract base for all warehouse agents

Implements the four-module agent structure from Basic Agentic AI.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from warehouse_architectures.environment import WarehouseEnvironment


class AgentType(Enum):
    """Type of agent."""
    SIMPLE_REFLEX = "simple_reflex"
    MODEL_BASED = "model_based"
    GOAL_BASED = "goal_based"
    UTILITY_BASED = "utility_based"


@dataclass
class AgentState:
    """Current state of an agent."""
    agent_id: str
    agent_type: str
    current_task: str
    status: str  # "idle" | "working" | "failed"
    deliberative_logic: bool  # True if agent has its own planning


@dataclass
class ActionResult:
    """Result of an action execution."""
    success: bool
    message: str
    data: dict[str, Any] | None = None


class BaseAgent(ABC):
    """
    Abstract base agent with perception, reasoning, action, optional learning.
    """

    def __init__(self, agent_id: str, agent_type: AgentType, env: WarehouseEnvironment):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.env = env
        self._status = "idle"
        self._current_task = ""

    @abstractmethod
    def perceive(self, environment: WarehouseEnvironment) -> dict[str, Any]:
        """Process environment into perceptions."""
        pass

    @abstractmethod
    def reason(self, perceptions: dict[str, Any]) -> tuple[str, str]:
        """Decide action. Returns (action_description, rationale)."""
        pass

    @abstractmethod
    def act(self, decision: tuple[str, str]) -> ActionResult:
        """Execute decision."""
        pass

    def get_state(self) -> AgentState:
        """Return current agent state."""
        return AgentState(
            agent_id=self.agent_id,
            agent_type=self.agent_type.value,
            current_task=self._current_task,
            status=self._status,
            deliberative_logic=self.agent_type in (AgentType.GOAL_BASED, AgentType.UTILITY_BASED),
        )

    def set_task(self, task: str) -> None:
        self._current_task = task
        self._status = "working" if task else "idle"

    def fail(self) -> None:
        self._status = "failed"
