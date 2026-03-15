"""Tools for meeting planning."""

from .calendar_tool import check_availability
from .venue_tool import search_venues
from .catering_tool import get_catering
from .booking_tool import book_venue

TOOLS = {
    "calendar_tool": check_availability,
    "venue_tool": search_venues,
    "catering_tool": get_catering,
    "booking_tool": book_venue,
}
