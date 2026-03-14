"""
Human-in-the-Loop — Full Robot Agent
"""

from config import MODEL, MAX_TOKENS
from environment.warehouse import WarehouseEnvironment, DeliveryTask
from human.human_supervisor import HumanSupervisor
from agent.skill_library import SkillLibrary
from agent.llm_client import LLMClient
from agent.controller import Controller, TaskResult


class WarehouseRobotAgent:
    """Full robot agent with Human-in-the-Loop support."""

    def __init__(self):
        self.env = WarehouseEnvironment()
        self.llm = LLMClient(model=MODEL, max_tokens=MAX_TOKENS)
        self.skills = SkillLibrary()
        self.human = HumanSupervisor()
        self.controller = Controller(
            self.llm,
            self.env,
            self.human,
            self.skills,
        )

    def execute_task(self, task: DeliveryTask) -> TaskResult:
        """Execute delivery task."""
        return self.controller.execute_task(task)
