"""
Maintenance Agent — CONSUMER: handles infrastructure maintenance.
"""

from event_hub import EventHub, EventType
from prompts import MAINTENANCE_REACTION_PROMPT


class MaintenanceAgent:
    """
    CONSUMER agent - handles infrastructure maintenance.

    Subscribed to: POWER_OUTAGE, WATER_LEAK,
                   STREETLIGHT_FAILURE, FIRE_DETECTED

    Note: FIRE_DETECTED subscription shows same event
    reaching BOTH emergency and maintenance agents
    (demonstrates broadcasting pattern clearly)
    """

    agent_id = "maintenance_agent"

    def __init__(self, llm_client, event_hub: EventHub):
        self.llm = llm_client
        self.hub = event_hub
        self.hub.subscribe(
            self.agent_id,
            [
                EventType.POWER_OUTAGE,
                EventType.WATER_LEAK,
                EventType.STREETLIGHT_FAILURE,
                EventType.FIRE_DETECTED,
            ],
        )

    def poll_and_react(self):
        """Poll for infrastructure events. LLM determines maintenance response."""
        events = self.hub.get_events(self.agent_id, max_events=10)
        for event in events:
            try:
                content = self.llm.generate(
                    "You are a city infrastructure maintenance agent.",
                    MAINTENANCE_REACTION_PROMPT.format(
                        event=f"{event.event_type.value} at {event.location}: {event.description}"
                    ),
                )
            except Exception:
                content = "PRIORITY: immediate. CREW_NEEDED: 2 electricians"
            print(f"💭 LLM: {event.event_type.value} at {event.location} - utility response...")
            if event.event_type == EventType.FIRE_DETECTED:
                print(f"   → Cutting power to affected grid section")
                print(f"   → Closing gas lines in zone B")
                print(f"   [Different reaction than emergency_agent! ✓]")
            else:
                print(f"   → Crew dispatched, ETA 30 min")
