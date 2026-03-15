"""Simulated tools for meeting planning."""

from .calendar_tool import check_availability
from .venue_tool import search_venues
from .catering_tool import get_catering
from .document_tool import create_proposal

TOOLS = {
    "check_availability": check_availability,
    "search_venues": search_venues,
    "get_catering": get_catering,
    "create_proposal": create_proposal,
}
