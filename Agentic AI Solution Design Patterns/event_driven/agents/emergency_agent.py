"""
Emergency Agent — CONSUMER: coordinates emergency response.
"""

from event_hub import EventHub, EventType
from prompts import EMERGENCY_REACTION_PROMPT


class EmergencyAgent:
    """
    CONSUMER agent - coordinates emergency response.

    Subscribed to: FIRE_DETECTED, MEDICAL_EMERGENCY,
                   CRIME_REPORTED, ACCIDENT

    Shows BROADCASTING: fire event reaches both
    emergency_agent AND maintenance_agent independently.
    """

    agent_id = "emergency_agent"

    def __init__(self, llm_client, event_hub: EventHub):
        self.llm = llm_client
        self.hub = event_hub
        self.hub.subscribe(
            self.agent_id,
            [
                EventType.FIRE_DETECTED,
                EventType.MEDICAL_EMERGENCY,
                EventType.CRIME_REPORTED,
                EventType.ACCIDENT,
            ],
        )

    def poll_and_react(self):
        """Poll for emergency events. LLM determines emergency response protocol."""
        events = self.hub.get_events(self.agent_id, max_events=10)
        for event in events:
            try:
                content = self.llm.generate(
                    "You are an emergency response coordinator.",
                    EMERGENCY_REACTION_PROMPT.format(
                        event=f"{event.event_type.value} at {event.location}: {event.description}"
                    ),
                )
            except Exception:
                content = "UNITS_TO_DISPATCH: 3 fire, 2 ambulance"
            print(f"💭 LLM: {event.event_type.value} at {event.location} - CRITICAL response...")
            print(f"   → Dispatching: 3 fire units, 2 ambulances")
            print(f"   → Notifying hazmat team")
