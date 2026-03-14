"""
Hybrid Agentic System

Parent handles high-level goals; agents have deliberative logic for local situations.
Implements Basic Agentic AI System Architectures — Hybrid.
"""

from typing import Any

from warehouse_architectures.environment import Task, TaskStatus, WarehouseEnvironment
from warehouse_architectures.agents.goal_based import GoalBasedAgent
from warehouse_architectures.agents.simple_reflex import SimpleReflexAgent
from warehouse_architectures.parent_system import ParentSystem

PREFIX = "[HYBRID]"


class HybridParentSystem(ParentSystem):
    """
    Hybrid parent: high-level goals only. Agents handle local situations.
    """

    def __init__(self, env: WarehouseEnvironment, goal_agents: list, reflex_agents: list):
        super().__init__(env)
        self.goal_agents = {a.agent_id: a for a in goal_agents}
        self.reflex_agents = {a.agent_id: a for a in reflex_agents}
        self._high_level_goal = ""

    def assign_or_delegate_tasks(self, tasks: list[Task]) -> None:
        """Parent breaks goals into sub-tasks for agents."""
        self._high_level_goal = "complete all deliveries"
        print(f"{PREFIX} Parent setting high-level goal: {self._high_level_goal}")
        for t in tasks:
            if t.assigned_agent:
                continue
            if "deliver" in t.task_type or "room" in t.target:
                agent_id = "Robot_A"
            elif "restock" in t.task_type or "shelf" in t.target:
                agent_id = "Robot_B"
            else:
                agent_id = "Robot_C"
            if agent_id in self.goal_agents or agent_id in self.reflex_agents:
                if agent_id not in self.env._failed_agents:
                    t.assigned_agent = agent_id
                    agent = self.goal_agents.get(agent_id) or self.reflex_agents.get(agent_id)
                    if hasattr(agent, "set_goal"):
                        agent.set_goal(f"{t.task_type}_{t.target}")
                    else:
                        agent.set_task(f"{t.task_type}_{t.target}")
                    print(f"{PREFIX} Parent delegating: {agent_id} → {t.task_type} {t.target}")

    def handle_conflict(self, conflict: dict[str, Any]) -> str:
        """Hybrid: capable agents try first, parent intervenes if needed."""
        return "Mixed (agents first, parent backup)"

    def handle_agent_failure(self, agent_id: str) -> str:
        """Hybrid: capable agents adapt, parent reallocates if needed."""
        self.env.inject_agent_failure(agent_id)
        if agent_id in self.goal_agents:
            self.goal_agents[agent_id].fail()
        if agent_id in self.reflex_agents:
            self.reflex_agents[agent_id].fail()
        print(f"{PREFIX} {agent_id} failed; capable agents adapting, parent reallocating if needed")
        return "Hybrid (agents adapt, parent reallocates)"

    def run_step(self) -> dict[str, Any]:
        """Mix of central direction + autonomous agent action."""
        for agent_id, agent in list(self.goal_agents.items()) + list(self.reflex_agents.items()):
            if agent_id in self.env._failed_agents:
                continue
            perceptions = agent.perceive(self.env)
            decision = agent.reason(perceptions)
            result = agent.act(decision)
            if "autonomously" in result.message or "self-resolved" in result.message:
                print(f"{PREFIX} {agent_id} autonomously handling locked door...")
                print(f"{PREFIX} {agent_id} self-resolved: entered keypad code")
            if result.success and agent._current_task:
                for t in self.env.active_tasks:
                    if t.assigned_agent == agent_id:
                        t.status = TaskStatus.COMPLETED
                        break
        pct = int(self.get_progress() * 100)
        print(f"{PREFIX} Parent monitoring: system {pct}% complete, no intervention")
        return {"progress": self.get_progress()}


class HybridAgenticSystem:
    """
    Hybrid architecture: parent high-level goals, agents handle local situations.
    Most realistic real-world architecture.
    """

    def __init__(self, env: WarehouseEnvironment):
        self.env = env
        self.goal_agents = [
            GoalBasedAgent("Robot_A", env),
            GoalBasedAgent("Robot_C", env),
        ]
        self.reflex_agents = [
            SimpleReflexAgent("Robot_B", env),
        ]
        self.parent_system = HybridParentSystem(
            env, self.goal_agents, self.reflex_agents
        )
        self._metrics = {
            "conflict_resolution": "Mixed",
            "failure_recovery": "Fast",
            "unexpected_events": "Flexible",
            "infrastructure": "Medium",
            "complexity": "Medium",
        }

    def set_high_level_goals(self, goals: list[Task]) -> None:
        """Parent sets system-wide objectives."""
        self.env.set_tasks(goals)
        self.env.active_agents = (
            [a.agent_id for a in self.goal_agents] +
            [a.agent_id for a in self.reflex_agents]
        )
        self.parent_system.assign_or_delegate_tasks(goals)

    def delegate_to_agents(self, goal: Task) -> None:
        """Parent breaks goals into sub-tasks for agents."""
        self.parent_system.assign_or_delegate_tasks([goal])

    def agents_handle_local_situations(self) -> None:
        """Each capable agent resolves own obstacles autonomously."""
        pass  # Handled in run_step

    def parent_intervenes_when_needed(self) -> None:
        """Parent steps in only for system-wide issues."""
        pass  # Handled in run_step

    def handle_agent_failure(self, agent_id: str) -> str:
        """Hybrid: capable agents adapt, parent reallocates if needed."""
        return self.parent_system.handle_agent_failure(agent_id)

    def run_step(self) -> dict[str, Any]:
        """Mix of central direction + autonomous agent action."""
        return self.parent_system.run_step()

    def handle_conflict(self, conflict: dict[str, Any]) -> str:
        return self.parent_system.handle_conflict(conflict)

    def generate_report(self) -> dict[str, Any]:
        return {
            "tasks_completed": f"{sum(1 for t in self.env.active_tasks if t.status == TaskStatus.COMPLETED)}/{len(self.env.active_tasks)}",
            "conflict_resolution": self._metrics["conflict_resolution"],
            "failure_recovery": self._metrics["failure_recovery"],
            "unexpected_events": self._metrics["unexpected_events"],
            "infrastructure": self._metrics["infrastructure"],
            "complexity": self._metrics["complexity"],
        }
