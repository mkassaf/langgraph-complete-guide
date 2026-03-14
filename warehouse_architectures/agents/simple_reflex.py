"""
Simple Reflex Agent — Condition-action rules only

No internal model, no planning. Reacts to current percepts.
Used in Centralized architecture.
"""

from warehouse_architectures.agents.base_agent import (
    BaseAgent,
    AgentState,
    AgentType,
    ActionResult,
)
from warehouse_architectures.environment import WarehouseEnvironment


class SimpleReflexAgent(BaseAgent):
    """
    Simple reflex agent: condition-action rules only.
    No deliberative logic — parent does all planning.
    """

    def __init__(self, agent_id: str, env: WarehouseEnvironment):
        super().__init__(agent_id, AgentType.SIMPLE_REFLEX, env)

    def perceive(self, environment: WarehouseEnvironment) -> dict[str, Any]:
        """Raw percept: current task only."""
        return {
            "current_task": self._current_task,
            "task_assigned": bool(self._current_task),
        }

    def reason(self, perceptions: dict[str, Any]) -> tuple[str, str]:
        """Condition-action: if task assigned, execute it."""
        if perceptions.get("task_assigned"):
            return ("execute_assigned", "Parent assigned task, executing")
        return ("wait", "No task assigned")

    def act(self, decision: tuple[str, str]) -> ActionResult:
        action, _ = decision
        if action == "execute_assigned":
            return ActionResult(True, f"{self.agent_id} executing {self._current_task}")
        return ActionResult(True, f"{self.agent_id} waiting")
