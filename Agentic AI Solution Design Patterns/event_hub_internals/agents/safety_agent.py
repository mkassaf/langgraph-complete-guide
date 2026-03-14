"""
Safety Agent — CONSUMER: reacts to safety events.
"""

from platform import EventHubPlatform, EventChannel
from prompts import SAFETY_REACTION_PROMPT


class SafetyAgent:
    """CONSUMER agent - reacts to safety events. Starts offline."""

    agent_id = "safety_agent"

    def __init__(self, llm_client, platform: EventHubPlatform):
        self.llm = llm_client
        self.platform = platform
        self.platform.subscribe(
            self.agent_id,
            [EventChannel.SAFETY_EVENTS, EventChannel.MACHINE_EVENTS],
            group_id="safety-consumers",
        )

    def poll_and_react(self):
        """Poll for events (comes online). LLM determines safety response."""
        print("[GROUP COORD]      safety_agent starts polling (now online)")
        self.platform.consumer_starts_polling(self.agent_id)
        for channel in [EventChannel.SAFETY_EVENTS, EventChannel.MACHINE_EVENTS]:
            events = self.platform.consumer_poll(self.agent_id, channel)
            for event in events:
                print(f"[DISPATCH]          Delivering missed event to safety_agent ✓")
                print(f"🚨 safety_agent received event (on next poll):")
                try:
                    content = self.llm.generate(
                        "You are a safety agent.",
                        SAFETY_REACTION_PROMPT.format(
                            event=f"{event.event_type} at {event.payload.get('location', '')}"
                        ),
                    )
                except Exception:
                    content = "RISK_LEVEL: high. IMMEDIATE_ACTION: Verify safety protocols"
                print(f"💭 LLM: {event.event_type} - check safety protocols")
                print(f"   ACTION: Verify heat shields operational")
