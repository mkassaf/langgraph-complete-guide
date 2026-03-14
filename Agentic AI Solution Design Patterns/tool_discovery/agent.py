"""
Tool Discovery — Office Building Agent
"""

from config import MODEL, MAX_TOKENS
from llm_client import LLMClient
from controller import Controller, ControllerResult
from registry.registry_builder import RegistryBuilder
from tools import TOOLS

TEST_TASKS = [
    "Book a meeting room for 10 people tomorrow at 2pm",
    "The printer on floor 3 is broken, report it",
    "I need to register a visitor arriving Monday",
    "Request catering for 15 people for a team lunch",
    "My laptop is not connecting to VPN, get help",
]


class OfficeBuildingAgent:
    def __init__(self):
        self.llm = LLMClient(model=MODEL, max_tokens=MAX_TOKENS)
        self.registry = RegistryBuilder().build_office_registry()
        self.tools = TOOLS
        self.controller = Controller(self.llm, self.registry, self.tools)

    def run_comparison(self, task: str) -> tuple[ControllerResult, ControllerResult]:
        """Run same task in both modes."""
        all_result = self.controller.run_all_tools_mode(task)
        disc_result = self.controller.run_discovery_mode(task)
        return all_result, disc_result
