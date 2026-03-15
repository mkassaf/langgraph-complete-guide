"""
Memory, Skill & Adaptive Action Patterns — Configuration
"""

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1000

PAST_MEETINGS = [
    {
        "meeting_id": "MTG-001",
        "user": "Ahmed",
        "request": "Team lunch for 10 people",
        "venue_chosen": "Innovation Suite",
        "catering": "Vegetarian Mediterranean",
        "outcome": "success",
        "user_feedback": "Perfect! Ahmed loves Innovation Suite",
    "tools_used": ["calendar_tool", "venue_tool", "catering_tool"],
    "tool_latencies": {"calendar_tool": 1.2, "venue_tool": 8.5, "catering_tool": 2.1, "booking_tool": 1.8},
    "successful_sequence": ["calendar_tool", "venue_tool", "catering_tool", "booking_tool"],
    },
    {
        "meeting_id": "MTG-002",
        "user": "Ahmed",
        "request": "Client presentation for 8 people",
        "venue_chosen": "Innovation Suite",
        "catering": "Vegetarian finger food",
        "outcome": "success",
        "user_feedback": "Ahmed confirmed Innovation Suite preference",
    "tools_used": ["calendar_tool", "venue_tool", "booking_tool"],
    "tool_latencies": {"calendar_tool": 1.1, "venue_tool": 9.2, "booking_tool": 1.5},
    "note": "venue_tool slow, booking_tool 6x faster for small groups",
    },
]
