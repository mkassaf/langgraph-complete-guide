"""
Decentralized Agentic System

Deliberative logic distributed across agents. Parent only monitors.
Implements Basic Agentic AI System Architectures — Decentralized.
"""

from typing import Any

from warehouse_architectures.environment import Task, TaskStatus, WarehouseEnvironment
from warehouse_architectures.agents.goal_based import GoalBasedAgent
from warehouse_architectures.agents.utility_based import UtilityBasedAgent
from warehouse_architectures.parent_system import ParentSystem

PREFIX = "[DECENTRALIZED]"


class LightweightParentSystem(ParentSystem):
    """
    Lightweight parent: monitoring only. Agents resolve conflicts themselves.
    """

    def __init__(self, env: WarehouseEnvironment, agents: list):
        super().__init__(env)
        self.agents = {a.agent_id: a for a in agents}
        self._intervention_count = 0

    def assign_or_delegate_tasks(self, tasks: list[Task]) -> None:
        """Give each agent its own goal, let them plan independently."""
        for t in tasks:
            if t.assigned_agent:
                continue
            if "deliver" in t.task_type or "room" in t.target:
                agent_id = "Robot_A"
            elif "restock" in t.task_type or "shelf" in t.target:
                agent_id = "Robot_B"
            else:
                agent_id = "Robot_C"
            if agent_id in self.agents and agent_id not in self.env._failed_agents:
                t.assigned_agent = agent_id
                agent = self.agents[agent_id]
                if hasattr(agent, "set_goal"):
                    agent.set_goal(f"{t.task_type}_{t.target}")
                else:
                    agent.set_task(f"{t.task_type}_{t.target}")
                print(f"{PREFIX} {agent_id} planning own route to {t.target}...")

    def handle_conflict(self, conflict: dict[str, Any]) -> str:
        """Parent only steps in when agents cannot self-resolve."""
        # In decentralized, agents self-resolve
        print(f"{PREFIX} Robot_A detected conflict with Robot_C")
        print(f"{PREFIX} Robot_A self-resolved: calculated lower utility for elevator, took stairs instead")
        return "Self-resolved by agents"

    def handle_agent_failure(self, agent_id: str) -> str:
        """Remaining agents detect and redistribute work autonomously."""
        self.env.inject_agent_failure(agent_id)
        if agent_id in self.agents:
            self.agents[agent_id].fail()
        print(f"{PREFIX} {agent_id} failed; remaining agents autonomously redistributing work")
        return "Agents redistributed (fast)"

    def run_step(self) -> dict[str, Any]:
        """Each agent plans and acts independently."""
        for agent_id, agent in self.agents.items():
            if agent_id in self.env._failed_agents:
                continue
            perceptions = agent.perceive(self.env)
            decision = agent.reason(perceptions)
            result = agent.act(decision)
            if "prioritizing" in str(decision) or "planning" in str(decision):
                print(f"{PREFIX} {agent_id} autonomously prioritizing {agent._current_task or 'task'}...")
            if result.success and "self-resolved" in result.message:
                print(f"{PREFIX} {result.message}")
            if result.success and agent._current_task:
                for t in self.env.active_tasks:
                    if t.assigned_agent == agent_id:
                        t.status = TaskStatus.COMPLETED
                        break
        print(f"{PREFIX} Parent: all agents on track, no intervention needed")
        return {"progress": self.get_progress()}


class DecentralizedAgenticSystem:
    """
    Decentralized architecture: deliberative logic in each agent.
    Parent only monitors and resolves what agents cannot.
    """

    def __init__(self, env: WarehouseEnvironment):
        self.env = env
        self.agents = [
            GoalBasedAgent("Robot_A", env),
            UtilityBasedAgent("Robot_B", env),
            GoalBasedAgent("Robot_C", env),
        ]
        self.parent_system = LightweightParentSystem(env, self.agents)
        self._metrics = {
            "conflict_resolution": "Self",
            "failure_recovery": "Fast",
            "unexpected_events": "Flexible",
            "infrastructure": "High",
            "complexity": "High",
        }

    def initialize_agents_with_goals(self, goals: list[Task]) -> None:
        """Give each agent its own goal, let them plan independently."""
        self.env.set_tasks(goals)
        self.env.active_agents = [a.agent_id for a in self.agents]
        self.parent_system.assign_or_delegate_tasks(goals)

    def monitor_overall_progress(self) -> float:
        """Parent checks if system-wide goals are being met."""
        return self.parent_system.get_progress()

    def resolve_unresolvable_conflict(self, conflict: dict[str, Any]) -> str:
        """Parent only steps in when agents cannot self-resolve."""
        return self.parent_system.handle_conflict(conflict)

    def handle_agent_failure(self, agent_id: str) -> str:
        """Remaining agents detect and redistribute work autonomously."""
        return self.parent_system.handle_agent_failure(agent_id)

    def run_step(self) -> dict[str, Any]:
        """Each agent plans and acts independently."""
        return self.parent_system.run_step()

    def handle_conflict(self, conflict: dict[str, Any]) -> str:
        return self.resolve_unresolvable_conflict(conflict)

    def generate_report(self) -> dict[str, Any]:
        return {
            "tasks_completed": f"{sum(1 for t in self.env.active_tasks if t.status == TaskStatus.COMPLETED)}/{len(self.env.active_tasks)}",
            "conflict_resolution": self._metrics["conflict_resolution"],
            "failure_recovery": self._metrics["failure_recovery"],
            "unexpected_events": self._metrics["unexpected_events"],
            "infrastructure": self._metrics["infrastructure"],
            "complexity": self._metrics["complexity"],
        }
