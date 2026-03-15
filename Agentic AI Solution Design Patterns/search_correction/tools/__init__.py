"""Tools for meeting planning."""

from .calendar_tool import check_availability
from .venue_tool import search_venues
from .catering_tool import get_catering
from .compliance_checker_tool import check_vendor_compliance

TOOLS = {
    "check_availability": check_availability,
    "search_venues": search_venues,
    "get_catering": get_catering,
    "compliance_checker": check_vendor_compliance,
}
