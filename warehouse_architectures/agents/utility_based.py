"""
Utility-Based Agent — Evaluates utility, has deliberative logic

Maximizes utility when choosing actions.
Used in Decentralized architecture.
"""

from warehouse_architectures.agents.base_agent import (
    BaseAgent,
    AgentType,
    ActionResult,
)
from warehouse_architectures.environment import WarehouseEnvironment


class UtilityBasedAgent(BaseAgent):
    """
    Utility-based agent: evaluates utility scores for options.
    Has deliberative logic — parent only monitors.
    """

    def __init__(self, agent_id: str, env: WarehouseEnvironment):
        super().__init__(agent_id, AgentType.UTILITY_BASED, env)

    def perceive(self, environment: WarehouseEnvironment) -> dict[str, Any]:
        """Full state for utility evaluation."""
        state = environment.get_system_state()
        return {
            "current_task": self._current_task,
            "resources": state.get("resources", {}),
            "elevator_available": not state.get("resources", {}).get("elevator", {}).get("in_use_by"),
            "power_outage": state.get("power_outage"),
        }

    def reason(self, perceptions: dict[str, Any]) -> tuple[str, str]:
        """Evaluate utility: elevator vs stairs."""
        elevator_util = 0.9 if perceptions.get("elevator_available") else 0.3
        stairs_util = 0.7  # Always available

        if elevator_util > stairs_util:
            return ("use_elevator", f"Utility: elevator={elevator_util} > stairs={stairs_util}")
        return ("use_stairs", f"Utility: stairs={stairs_util} chosen (elevator conflict)")

    def act(self, decision: tuple[str, str]) -> ActionResult:
        action, rationale = decision
        if action == "use_stairs":
            return ActionResult(
                True,
                f"{self.agent_id} self-resolved: calculated lower utility for elevator, took stairs instead"
            )
        if action == "use_elevator":
            return ActionResult(True, f"{self.agent_id} using elevator (highest utility)")
        return ActionResult(True, f"{self.agent_id} executing")
