"""
Model-Based Reflex Agent — Internal model + rules

Maintains internal state, no full planning.
Used in Centralized architecture.
"""

from warehouse_architectures.agents.base_agent import (
    BaseAgent,
    AgentType,
    ActionResult,
)
from warehouse_architectures.environment import WarehouseEnvironment


class ModelBasedReflexAgent(BaseAgent):
    """
    Model-based reflex agent: internal model + condition-action rules.
    Tracks state but does not plan — parent does planning.
    """

    def __init__(self, agent_id: str, env: WarehouseEnvironment):
        super().__init__(agent_id, AgentType.MODEL_BASED, env)
        self._internal_model: dict[str, str] = {}  # task -> last_action

    def perceive(self, environment: WarehouseEnvironment) -> dict[str, Any]:
        """Percept + internal model state."""
        state = environment.get_system_state()
        return {
            "current_task": self._current_task,
            "task_assigned": bool(self._current_task),
            "internal_state": self._internal_model.copy(),
            "power_outage": state.get("power_outage"),
        }

    def reason(self, perceptions: dict[str, Any]) -> tuple[str, str]:
        """Model + rules: consider internal state when deciding."""
        if perceptions.get("power_outage") and "B" in str(perceptions.get("power_outage", "")):
            return ("avoid_section_b", "Power outage in B, using model to avoid")
        if perceptions.get("task_assigned"):
            self._internal_model[self._current_task] = "in_progress"
            return ("execute_assigned", "Model updated, executing")
        return ("wait", "No task, waiting")

    def act(self, decision: tuple[str, str]) -> ActionResult:
        action, _ = decision
        if action == "execute_assigned":
            return ActionResult(True, f"{self.agent_id} executing {self._current_task}")
        if action == "avoid_section_b":
            return ActionResult(True, f"{self.agent_id} taking alternate route (avoiding B)")
        return ActionResult(True, f"{self.agent_id} waiting")
