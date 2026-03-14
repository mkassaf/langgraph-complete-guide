"""
Centralized Agentic System

Parent holds ALL deliberative logic. Agents are simple/model-based reflex only.
Implements Basic Agentic AI System Architectures — Centralized.
"""

from typing import Any

from warehouse_architectures.environment import Task, TaskStatus, WarehouseEnvironment
from warehouse_architectures.agents.simple_reflex import SimpleReflexAgent
from warehouse_architectures.agents.model_based import ModelBasedReflexAgent
from warehouse_architectures.parent_system import ParentSystem

PREFIX = "[CENTRALIZED]"


class CentralParentSystem(ParentSystem):
    """
    Central parent: does all planning, assigns tasks to reflex agents.
    """

    def __init__(self, env: WarehouseEnvironment, agents: list):
        super().__init__(env)
        self.agents = {a.agent_id: a for a in agents}
        self._assignments: dict[str, str] = {}

    def assign_or_delegate_tasks(self, tasks: list[Task]) -> None:
        """Parent plans and assigns each task to an agent."""
        for t in tasks:
            if t.assigned_agent:
                continue
            # Parent assigns: A=deliver, B=restock, C=pickup
            if "deliver" in t.task_type or "room" in t.target:
                agent_id = "Robot_A"
            elif "restock" in t.task_type or "shelf" in t.target:
                agent_id = "Robot_B"
            else:
                agent_id = "Robot_C"
            if agent_id in self.agents and agent_id not in self.env._failed_agents:
                t.assigned_agent = agent_id
                self.agents[agent_id].set_task(f"{t.task_type}_{t.target}")
                self._assignments[agent_id] = t.task_id
                print(f"{PREFIX} Assigning: {agent_id} → {t.task_type}_{t.target}")

    def handle_conflict(self, conflict: dict[str, Any]) -> str:
        """Parent resolves resource conflicts."""
        resource = conflict.get("resource", "elevator")
        contenders = conflict.get("contenders", [])
        # Parent gives Robot_A priority
        winner = "Robot_A" if "Robot_A" in contenders else contenders[0] if contenders else ""
        resolution = f"{winner} gets priority"
        print(f"{PREFIX} Conflict detected: {' and '.join(contenders)} need {resource}")
        print(f"{PREFIX} Parent resolved: {resolution}")
        return resolution

    def handle_agent_failure(self, agent_id: str) -> str:
        """Parent detects and reassigns failed agent tasks."""
        self.env.inject_agent_failure(agent_id)
        if agent_id in self.agents:
            self.agents[agent_id].fail()
        # Parent reassigns to another agent (slow - centralized)
        for t in self.env.active_tasks:
            if t.assigned_agent == agent_id:
                t.status = TaskStatus.PENDING
                t.assigned_agent = None
        print(f"{PREFIX} Agent failure: {agent_id} crashed, parent reassigning tasks...")
        return "Parent reassigning (slow)"

    def run_step(self) -> dict[str, Any]:
        """Parent decides everything, agents just execute."""
        self.assign_or_delegate_tasks(self.env.active_tasks)
        for agent_id, agent in self.agents.items():
            if agent_id in self.env._failed_agents:
                continue
            if agent._current_task:
                perceptions = agent.perceive(self.env)
                decision = agent.reason(perceptions)
                result = agent.act(decision)
                if result.success and "executing" in result.message:
                    for t in self.env.active_tasks:
                        if t.assigned_agent == agent_id:
                            t.status = TaskStatus.COMPLETED
                            break
        return {"progress": self.get_progress()}


class CentralizedAgenticSystem:
    """
    Centralized architecture: parent holds ALL deliberative logic.
    Agents are simple/model-based reflex only.
    """

    def __init__(self, env: WarehouseEnvironment):
        self.env = env
        self.agents = [
            SimpleReflexAgent("Robot_A", env),
            ModelBasedReflexAgent("Robot_B", env),
            SimpleReflexAgent("Robot_C", env),
        ]
        self.parent_system = CentralParentSystem(env, self.agents)
        self._metrics: dict[str, Any] = {
            "tasks_completed": 0,
            "conflict_resolution": "Parent",
            "failure_recovery": "Slow",
            "unexpected_events": "Rigid",
            "infrastructure": "Low",
            "complexity": "Low",
        }

    def assign_tasks(self, tasks: list[Task]) -> None:
        """Parent plans and assigns each task to an agent."""
        self.env.set_tasks(tasks)
        self.env.active_agents = [a.agent_id for a in self.agents]
        print(f"{PREFIX} Parent analyzing all tasks...")
        self.parent_system.assign_or_delegate_tasks(tasks)

    def coordinate_agents(self) -> None:
        """Parent manages all inter-agent communication."""
        print(f"{PREFIX} Parent coordinating agents...")

    def handle_conflict(self, conflict: dict[str, Any]) -> str:
        """Parent resolves resource conflicts."""
        return self.parent_system.handle_conflict(conflict)

    def handle_agent_failure(self, agent_id: str) -> str:
        """Parent detects and reassigns failed agent tasks."""
        return self.parent_system.handle_agent_failure(agent_id)

    def run_step(self) -> dict[str, Any]:
        """Parent decides everything, agents just execute."""
        return self.parent_system.run_step()

    def generate_report(self) -> dict[str, Any]:
        return {
            "tasks_completed": f"{sum(1 for t in self.env.active_tasks if t.status == TaskStatus.COMPLETED)}/{len(self.env.active_tasks)}",
            "conflict_resolution": self._metrics["conflict_resolution"],
            "failure_recovery": self._metrics["failure_recovery"],
            "unexpected_events": self._metrics["unexpected_events"],
            "infrastructure": self._metrics["infrastructure"],
            "complexity": self._metrics["complexity"],
        }
