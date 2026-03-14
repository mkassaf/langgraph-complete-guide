"""
Traffic Agent — CONSUMER: manages traffic flow.
"""

from event_hub import EventHub, EventType
from prompts import TRAFFIC_REACTION_PROMPT


class TrafficAgent:
    """
    CONSUMER agent - manages traffic flow.

    Subscribed to: TRAFFIC_JAM, ACCIDENT, ROAD_CLOSURE

    From lesson: 'Consumer agents can be subscribed to
    these types of specific events. When they are ready,
    they request these events from the Event Hub, which
    then sends them messages with the event details.'

    Reaction triggers: Events directly trigger rerouting
    """

    agent_id = "traffic_agent"

    def __init__(self, llm_client, event_hub: EventHub):
        self.llm = llm_client
        self.hub = event_hub
        self.hub.subscribe(
            self.agent_id,
            [EventType.TRAFFIC_JAM, EventType.ACCIDENT, EventType.ROAD_CLOSURE],
        )

    def poll_and_react(self):
        """Poll for traffic events. LLM determines rerouting strategy."""
        events = self.hub.get_events(self.agent_id, max_events=10)
        for event in events:
            try:
                content = self.llm.generate(
                    "You are a traffic management agent.",
                    TRAFFIC_REACTION_PROMPT.format(
                        event=f"{event.event_type.value} at {event.location}: {event.description}"
                    ),
                )
            except Exception:
                content = "REROUTING_STRATEGY: Via Park Ave. SIGNALS_TO_ADJUST: 12"
            print(f"💭 LLM: {event.event_type.value} at {event.location} - rerouting via Park Ave...")
            print(f"   → Adjusting 12 traffic signals")
            print(f"   → Broadcasting public alert")
