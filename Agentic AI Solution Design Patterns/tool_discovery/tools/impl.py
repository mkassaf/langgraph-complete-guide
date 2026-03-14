"""
Tool implementations — simulated office building tools.
Each returns realistic fake data.
"""


def _room_booking(capacity: int = 10, date: str = "tomorrow", time: str = "14:00", **kwargs) -> dict:
    return {"success": True, "room": "Room 303", "message": f"Room 303 booked for {capacity} people at {time} on {date}"}


def _desk_booking(date: str = "tomorrow", floor: int = 3, **kwargs) -> dict:
    return {"success": True, "desk": f"Desk F3-{floor}12", "message": f"Desk reserved on {date}"}


def _parking_booking(date: str = "tomorrow", duration: str = "8h", **kwargs) -> dict:
    return {"success": True, "spot": "P-42", "message": f"Parking reserved for {duration}"}


def _equipment_loan(item: str = "projector", date: str = "tomorrow", **kwargs) -> dict:
    return {"success": True, "item": item, "message": f"{item} reserved for {date}"}


def _it_ticket(issue: str = "", location: str = "", priority: str = "medium", **kwargs) -> dict:
    return {"success": True, "ticket_id": "IT-2026-0042", "message": f"Ticket created. Estimated response: 2 hours."}


def _password_reset(user_id: str = "", **kwargs) -> dict:
    return {"success": True, "message": "Password reset link sent to user email"}


def _software_request(software_name: str = "", reason: str = "", **kwargs) -> dict:
    return {"success": True, "request_id": "SW-789", "message": "Software request submitted for approval"}


def _vpn_access(user_id: str = "", action: str = "troubleshoot", **kwargs) -> dict:
    return {"success": True, "message": "VPN connection reset. Please try reconnecting."}


def _hardware_request(item: str = "", reason: str = "", **kwargs) -> dict:
    return {"success": True, "request_id": "HW-456", "message": "Hardware request submitted"}


def _maintenance(issue: str = "", location: str = "", **kwargs) -> dict:
    return {"success": True, "ticket_id": "MNT-123", "message": "Maintenance ticket created. ETA: 4 hours."}


def _cleaning(area: str = "", type: str = "standard", **kwargs) -> dict:
    return {"success": True, "message": f"Cleaning scheduled for {area or 'requested area'}"}


def _temperature(room: str = "", temp: int = 22, **kwargs) -> dict:
    return {"success": True, "message": f"Room {room} temperature set to {temp}°C"}


def _lighting(room: str = "", level: str = "medium", **kwargs) -> dict:
    return {"success": True, "message": f"Lighting in {room} set to {level}"}


def _printer_status(location: str = "", **kwargs) -> dict:
    return {"success": True, "status": "operational", "paper": "80%", "toner": "60%"}


def _supply_request(items: list | None = None, department: str = "", **kwargs) -> dict:
    return {"success": True, "order_id": "SUP-999", "message": "Supply order submitted"}


def _visitor(name: str = "", company: str = "", date: str = "", host: str = "", **kwargs) -> dict:
    return {"success": True, "badge_id": "V-2026-001", "message": f"Visitor {name} registered for {date}"}


def _access(user_id: str = "", action: str = "", **kwargs) -> dict:
    return {"success": True, "message": "Access updated"}


def _expense(amount: float = 0, category: str = "", receipt: str = "", **kwargs) -> dict:
    return {"success": True, "report_id": "EXP-555", "message": "Expense report submitted"}


def _hr_request(request_type: str = "", details: str = "", **kwargs) -> dict:
    return {"success": True, "request_id": "HR-111", "message": "HR request submitted"}


def _incident(incident_type: str = "", location: str = "", details: str = "", **kwargs) -> dict:
    return {"success": True, "report_id": "SEC-777", "message": "Incident report filed"}


def _cctv(location: str = "", date: str = "", time: str = "", **kwargs) -> dict:
    return {"success": True, "request_id": "CCTV-333", "message": "CCTV review request submitted"}


def _lost_found(item: str = "", location: str = "", type: str = "lost", **kwargs) -> dict:
    return {"success": True, "report_id": "LF-222", "message": f"{type.capitalize()} item report filed"}


def _catering(guests: int = 15, date: str = "", meal_type: str = "lunch", **kwargs) -> dict:
    return {"success": True, "order_id": "CAT-888", "message": f"Catering for {guests} ordered for {meal_type}"}


def _coffee(location: str = "", action: str = "brew", **kwargs) -> dict:
    return {"success": True, "message": "Coffee brewing"}


TOOLS = {
    "room_booking_tool": _room_booking,
    "desk_booking_tool": _desk_booking,
    "parking_booking_tool": _parking_booking,
    "equipment_loan_tool": _equipment_loan,
    "it_ticket_tool": _it_ticket,
    "password_reset_tool": _password_reset,
    "software_request_tool": _software_request,
    "vpn_access_tool": _vpn_access,
    "hardware_request_tool": _hardware_request,
    "maintenance_request_tool": _maintenance,
    "cleaning_request_tool": _cleaning,
    "temperature_control_tool": _temperature,
    "lighting_control_tool": _lighting,
    "printer_status_tool": _printer_status,
    "supply_request_tool": _supply_request,
    "visitor_management_tool": _visitor,
    "access_control_tool": _access,
    "expense_tool": _expense,
    "hr_request_tool": _hr_request,
    "incident_report_tool": _incident,
    "cctv_request_tool": _cctv,
    "lost_found_tool": _lost_found,
    "catering_order_tool": _catering,
    "coffee_machine_tool": _coffee,
}
