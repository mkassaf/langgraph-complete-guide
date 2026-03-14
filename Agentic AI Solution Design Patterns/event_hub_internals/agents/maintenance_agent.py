"""
Maintenance Agent — CONSUMER: reacts to machine events.
"""

from platform import EventHubPlatform, EventChannel
from prompts import MAINTENANCE_REACTION_PROMPT


class MaintenanceAgent:
    """CONSUMER agent - reacts to machine events."""

    agent_id = "maintenance_agent"

    def __init__(self, llm_client, platform: EventHubPlatform):
        self.llm = llm_client
        self.platform = platform
        self.platform.subscribe(
            self.agent_id,
            [EventChannel.MACHINE_EVENTS, EventChannel.QUALITY_EVENTS],
            group_id="machine-consumers",
        )

    def poll_and_react(self):
        """Poll for events. LLM determines maintenance response."""
        self.platform.consumer_starts_polling(self.agent_id)
        for channel in [EventChannel.MACHINE_EVENTS, EventChannel.QUALITY_EVENTS]:
            events = self.platform.consumer_poll(self.agent_id, channel)
            for event in events:
                print(f"🔧 maintenance_agent received event:")
                try:
                    content = self.llm.generate(
                        "You are a maintenance agent.",
                        MAINTENANCE_REACTION_PROMPT.format(
                            events=str(event.payload),
                            event_type=event.event_type,
                        ),
                    )
                except Exception:
                    content = "IMMEDIATE_ACTION: Dispatch crew. ESTIMATED_FIX_TIME: 15 min"
                print(f"💭 LLM: {event.event_type} at {event.payload.get('location', '')} - schedule inspection")
                print(f"   ACTION: Dispatch maintenance crew, ETA 15 minutes")
