"""
Goal-Based Agent — Plans own route, has deliberative logic

Creates multi-step plans to reach goals.
Used in Decentralized and Hybrid architectures.
"""

from warehouse_architectures.agents.base_agent import (
    BaseAgent,
    AgentType,
    ActionResult,
)
from warehouse_architectures.environment import WarehouseEnvironment


class GoalBasedAgent(BaseAgent):
    """
    Goal-based agent: plans own route to goal.
    Has deliberative logic — parent only monitors.
    """

    def __init__(self, agent_id: str, env: WarehouseEnvironment):
        super().__init__(agent_id, AgentType.GOAL_BASED, env)
        self._plan: list[str] = []
        self._goal: str = ""

    def perceive(self, environment: WarehouseEnvironment) -> dict[str, Any]:
        """Full state for planning."""
        state = environment.get_system_state()
        return {
            "current_task": self._current_task,
            "goal": self._goal or self._current_task,
            "resources": state.get("resources", {}),
            "power_outage": state.get("power_outage"),
            "conflict_possible": "elevator" in str(state),
        }

    def reason(self, perceptions: dict[str, Any]) -> tuple[str, str]:
        """Plan multi-step route to goal."""
        goal = perceptions.get("goal") or self._current_task
        if not goal:
            return ("wait", "No goal set")

        # Build plan
        self._plan = ["move_to_target", "execute_task", "complete"]
        if perceptions.get("power_outage"):
            self._plan.insert(0, "avoid_section_b")
        if perceptions.get("conflict_possible"):
            # Self-resolve: take stairs instead of elevator
            return ("use_stairs", "Planned route: avoiding elevator conflict, using stairs")
        return ("execute_plan", f"Planning own route to {goal}")

    def act(self, decision: tuple[str, str]) -> ActionResult:
        action, rationale = decision
        if action == "use_stairs":
            return ActionResult(True, f"{self.agent_id} self-resolved: took stairs instead of elevator")
        if action == "execute_plan":
            return ActionResult(True, f"{self.agent_id} executing plan toward goal")
        if action == "avoid_section_b":
            return ActionResult(True, f"{self.agent_id} autonomously rerouting around section B")
        return ActionResult(True, f"{self.agent_id} waiting")

    def set_goal(self, goal: str) -> None:
        self._goal = goal
        self.set_task(goal)
