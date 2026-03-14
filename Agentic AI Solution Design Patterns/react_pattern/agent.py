"""
ReAct Pattern — Meeting Planner Agent

Full ReAct agent combining Controller + LLM + Tools.
"""

from config import MODEL, MAX_TOKENS
from llm_client import LLMClient
from controller import Controller, ReactResult
from tools.calendar_tool import CalendarTool
from tools.venue_tool import VenueSearchTool
from tools.catering_tool import CateringTool
from tools.document_tool import DocumentTool


class MeetingPlannerAgent:
    """
    Full ReAct agent for planning team offsite meetings.
    Combines Controller + LLM + Tools.
    """

    def __init__(self):
        self.llm = LLMClient(model=MODEL, max_tokens=MAX_TOKENS)
        self.tools = [
            CalendarTool(),
            VenueSearchTool(),
            CateringTool(),
            DocumentTool(),
        ]
        self.controller = Controller(self.llm, self.tools)

    def plan_meeting(self, request: str) -> ReactResult:
        """Run full ReAct loop to plan the meeting."""
        return self.controller.run_react_loop(request)
