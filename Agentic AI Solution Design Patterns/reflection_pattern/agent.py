"""
Reflection Pattern — Meeting Planner Agent

Demonstrates all three Reflection scenarios.
"""

from config import MODEL, MAX_TOKENS
from llm_client import LLMClient
from controller import Controller, ControllerResult
from tools.calendar_tool import CalendarTool
from tools.venue_tool import VenueSearchTool
from tools.catering_tool import CateringTool
from tools.document_tool import DocumentTool


class MeetingPlannerAgent:
    """Demonstrates all three Reflection scenarios."""

    def __init__(self):
        self.llm = LLMClient(model=MODEL, max_tokens=MAX_TOKENS)
        self.tools = {
            "calendar_tool": CalendarTool(),
            "venue_search_tool": VenueSearchTool(),
            "catering_tool": CateringTool(),
            "document_tool": DocumentTool(),
        }
        self.controller = Controller(self.llm, self.tools)

    def demo_cot_with_reflection(self, request: str) -> ControllerResult:
        """Scenario 1: CoT output improved by reflection."""
        return self.controller.run_with_cot_reflection(request)

    def demo_react_with_reflection(self, request: str) -> ControllerResult:
        """Scenario 2: ReAct errors caught and fixed by reflection."""
        return self.controller.run_with_react_reflection(request)

    def demo_pattern_switch(self, request: str) -> ControllerResult:
        """Scenario 3: Simple prompt → reflection → switch to ReAct."""
        return self.controller.run_with_pattern_switch(request)
