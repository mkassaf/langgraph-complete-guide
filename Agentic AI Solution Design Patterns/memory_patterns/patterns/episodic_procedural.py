"""
Pattern 1: Episodic and Procedural Memory

From lesson: 'provides a specific structured mechanism for an LLM-enabled
agent to be able to store and retrieve information over a long period'

Demonstrates the STORAGE side of memory.
"""


class EpisodicProceduralPattern:
    def __init__(self, memory_module):
        self.memory = memory_module

    def run_meeting_session(
        self,
        request: str,
        user_id: str,
        tools: dict,
        llm_client,
    ) -> dict:
        """Run a meeting planning session."""
        r1 = tools["calendar_tool"](15, 3)
        r2 = tools["venue_tool"](15, r1.get("available_dates", ["18th"]))
        r3 = tools["catering_tool"](15, "Innovation Suite", "vegetarian")
        r4 = tools["booking_tool"]("Innovation Suite", "18th", 15)
        return {
            "request": request,
            "user": user_id,
            "venue_chosen": "Innovation Suite",
            "catering": "Vegetarian Mediterranean",
            "outcome": "success",
            "user_feedback": "Perfect! Ahmed loves Innovation Suite",
            "tools_used": ["calendar_tool", "venue_tool", "catering_tool", "booking_tool"],
            "tool_latencies": {"calendar": 1.2, "venue": 9.2, "catering": 2.1, "booking": 1.8},
            "successful_sequence": ["calendar_tool", "venue_tool", "catering_tool", "booking_tool"],
        }

    def store_memories_after_session(self, session_data: dict):
        """After session: store both memory types."""
        print("\n" + "═" * 42)
        print("MEMORY STORAGE (Episodic + Procedural)")
        print("═" * 42)
        print("Session complete. Storing memories...")
        self.memory.store_session(session_data)
