"""
Registry Builder — Populates the tool registry.

Represents the work of AI engineers maintaining the registry.
"""

from registry.tool_registry import ToolRegistry
from registry.tool_spec import ToolSpec


def _spec(
    id: str,
    name: str,
    category: str,
    description: str,
    use_cases: list[str],
    params: dict,
    returns: str,
    example: str,
    perms: list[str] | None = None,
) -> ToolSpec:
    return ToolSpec(
        id=id,
        name=name,
        category=category,
        description=description,
        use_cases=use_cases,
        parameters=params,
        returns=returns,
        example_usage=example,
        permissions_required=perms or [],
    )


class RegistryBuilder:
    """Populates the tool registry."""

    def build_office_registry(self) -> ToolRegistry:
        """Register 24 office tools across categories."""
        r = ToolRegistry()

        # BOOKING (4)
        r.register_tool(_spec(
            "room_booking", "room_booking_tool", "booking",
            "Book meeting rooms by capacity, date, and time",
            ["book room", "reserve meeting room", "schedule meeting"],
            {"capacity": "int", "date": "str", "time": "str"},
            "Booking confirmation with room number",
            "room_booking_tool(capacity=10, date='tomorrow', time='14:00')",
        ))
        r.register_tool(_spec(
            "desk_booking", "desk_booking_tool", "booking",
            "Reserve hot desks for flexible seating",
            ["reserve desk", "book desk", "hot desk"],
            {"date": "str", "floor": "int"},
            "Desk reservation confirmation",
            "desk_booking_tool(date='tomorrow', floor=3)",
        ))
        r.register_tool(_spec(
            "parking_booking", "parking_booking_tool", "booking",
            "Reserve parking spots in building garage",
            ["parking", "reserve parking", "parking spot"],
            {"date": "str", "duration": "str"},
            "Parking spot confirmation",
            "parking_booking_tool(date='tomorrow', duration='8h')",
        ))
        r.register_tool(_spec(
            "equipment_loan", "equipment_loan_tool", "booking",
            "Borrow projectors, laptops, and other equipment",
            ["borrow equipment", "projector", "equipment for meeting"],
            {"item": "str", "date": "str"},
            "Equipment loan confirmation",
            "equipment_loan_tool(item='projector', date='tomorrow')",
        ))

        # IT (5)
        r.register_tool(_spec(
            "it_ticket", "it_ticket_tool", "IT",
            "Create IT support tickets for technical issues",
            ["IT support", "report issue", "technical problem", "printer broken"],
            {"issue": "str", "location": "str", "priority": "str"},
            "Ticket ID and estimated response time",
            "it_ticket_tool(issue='printer broken', location='floor 3')",
        ))
        r.register_tool(_spec(
            "password_reset", "password_reset_tool", "IT",
            "Reset user passwords",
            ["password", "reset password", "locked out"],
            {"user_id": "str"},
            "Password reset confirmation",
            "password_reset_tool(user_id='john')",
        ))
        r.register_tool(_spec(
            "software_request", "software_request_tool", "IT",
            "Request new software installation",
            ["software", "install software", "new app"],
            {"software_name": "str", "reason": "str"},
            "Request ID",
            "software_request_tool(software_name='Slack')",
        ))
        r.register_tool(_spec(
            "vpn_access", "vpn_access_tool", "IT",
            "Manage VPN access and connection issues",
            ["VPN", "remote access", "cannot connect", "laptop not connecting"],
            {"user_id": "str", "action": "str"},
            "VPN status or fix applied",
            "vpn_access_tool(user_id='john', action='troubleshoot')",
        ))
        r.register_tool(_spec(
            "hardware_request", "hardware_request_tool", "IT",
            "Request new hardware (laptop, monitor, etc.)",
            ["hardware", "new laptop", "monitor"],
            {"item": "str", "reason": "str"},
            "Request ID",
            "hardware_request_tool(item='laptop')",
        ))

        # FACILITIES (6)
        r.register_tool(_spec(
            "maintenance", "maintenance_request_tool", "facilities",
            "Report maintenance issues (broken equipment, leaks, etc.)",
            ["maintenance", "broken", "repair", "fix"],
            {"issue": "str", "location": "str"},
            "Maintenance ticket ID",
            "maintenance_request_tool(issue='leak', location='room 301')",
        ))
        r.register_tool(_spec(
            "cleaning", "cleaning_request_tool", "facilities",
            "Request cleaning for rooms or areas",
            ["cleaning", "clean room", "vacuum"],
            {"area": "str", "type": "str"},
            "Cleaning scheduled",
            "cleaning_request_tool(area='room 303')",
        ))
        r.register_tool(_spec(
            "temperature", "temperature_control_tool", "facilities",
            "Adjust room temperature",
            ["temperature", "too cold", "too hot", "AC", "heating"],
            {"room": "str", "temp": "int"},
            "Temperature updated",
            "temperature_control_tool(room='303', temp=22)",
        ))
        r.register_tool(_spec(
            "lighting", "lighting_control_tool", "facilities",
            "Adjust room lighting",
            ["lights", "lighting", "dim", "bright"],
            {"room": "str", "level": "str"},
            "Lighting updated",
            "lighting_control_tool(room='303', level='dim')",
        ))
        r.register_tool(_spec(
            "printer_status", "printer_status_tool", "facilities",
            "Check printer status and paper levels",
            ["printer", "printer status", "paper", "toner"],
            {"location": "str"},
            "Printer status and supplies",
            "printer_status_tool(location='floor 3')",
        ))
        r.register_tool(_spec(
            "supply_request", "supply_request_tool", "facilities",
            "Request office supplies (paper, pens, etc.)",
            ["supplies", "office supplies", "paper", "pens"],
            {"items": "list", "department": "str"},
            "Supply order ID",
            "supply_request_tool(items=['paper'], department='IT')",
        ))

        # ADMIN (4)
        r.register_tool(_spec(
            "visitor", "visitor_management_tool", "admin",
            "Register and manage building visitors",
            ["visitor", "register visitor", "guest", "arriving"],
            {"name": "str", "company": "str", "date": "str", "host": "str"},
            "Visitor badge ID",
            "visitor_management_tool(name='John', date='Monday')",
        ))
        r.register_tool(_spec(
            "access", "access_control_tool", "admin",
            "Manage building access and badges",
            ["access", "badge", "door access"],
            {"user_id": "str", "action": "str"},
            "Access status",
            "access_control_tool(user_id='john', action='grant')",
        ))
        r.register_tool(_spec(
            "expense", "expense_tool", "admin",
            "Submit expense reports",
            ["expense", "expense report", "reimbursement"],
            {"amount": "float", "category": "str", "receipt": "str"},
            "Expense report ID",
            "expense_tool(amount=50, category='meals')",
        ))
        r.register_tool(_spec(
            "hr_request", "hr_request_tool", "admin",
            "Submit HR requests (leave, benefits, etc.)",
            ["HR", "human resources", "leave", "benefits"],
            {"request_type": "str", "details": "str"},
            "HR request ID",
            "hr_request_tool(request_type='leave')",
        ))

        # SECURITY (3)
        r.register_tool(_spec(
            "incident", "incident_report_tool", "security",
            "Report security incidents",
            ["security", "incident", "suspicious"],
            {"incident_type": "str", "location": "str", "details": "str"},
            "Incident report ID",
            "incident_report_tool(incident_type='unauthorized')",
        ))
        r.register_tool(_spec(
            "cctv", "cctv_request_tool", "security",
            "Request CCTV footage review",
            ["CCTV", "camera", "footage", "surveillance"],
            {"location": "str", "date": "str", "time": "str"},
            "Request ID",
            "cctv_request_tool(location='lobby')",
        ))
        r.register_tool(_spec(
            "lost_found", "lost_found_tool", "security",
            "Report lost or found items",
            ["lost", "found", "lost and found"],
            {"item": "str", "location": "str", "type": "str"},
            "Report ID",
            "lost_found_tool(item='keys', type='lost')",
        ))

        # CATERING (2)
        r.register_tool(_spec(
            "catering", "catering_order_tool", "catering",
            "Order catering for meetings and events",
            ["catering", "food", "lunch", "team lunch", "order food"],
            {"guests": "int", "date": "str", "meal_type": "str"},
            "Catering order confirmation",
            "catering_order_tool(guests=15, date='Friday', meal_type='lunch')",
        ))
        r.register_tool(_spec(
            "coffee", "coffee_machine_tool", "catering",
            "Control smart coffee machines",
            ["coffee", "espresso", "machine"],
            {"location": "str", "action": "str"},
            "Coffee status",
            "coffee_machine_tool(location='floor 2', action='brew')",
        ))

        return r
