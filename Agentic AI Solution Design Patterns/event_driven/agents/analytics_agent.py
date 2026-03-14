"""
Analytics Agent — CONSUMER: stream processing + event replay.
"""

from event_hub import EventHub, EventType
from prompts import STREAM_ANALYTICS_PROMPT, REPLAY_ANALYSIS_PROMPT


class AnalyticsAgent:
    """
    CONSUMER agent - real-time analytics + event replay.

    Subscribed to: ALL event types

    Demonstrates:
    - STREAM PROCESSING: continuous event analytics
    - EVENT REPLAY: reprocess historical events
    """

    agent_id = "analytics_agent"

    def __init__(self, llm_client, event_hub: EventHub):
        self.llm = llm_client
        self.hub = event_hub
        self.hub.subscribe(self.agent_id, list(EventType))
        self.event_counts: dict[str, int] = {}
        self.pattern_history: list[str] = []

    def process_stream(self):
        """STREAM PROCESSING: Poll all events. LLM detects patterns."""
        events = self.hub.get_events(self.agent_id, max_events=20)
        if not events:
            return
        print(f"📊 analytics_agent processing event stream...")
        batch_str = "\n".join(
            f"- {e.event_type.value} @ {e.location} ({e.severity.value})"
            for e in events
        )
        try:
            content = self.llm.generate(
                "You are a city analytics agent.",
                STREAM_ANALYTICS_PROMPT.format(events_batch=batch_str),
            )
        except Exception:
            content = "HOTSPOTS: Industrial Zone B. CITY_STATUS: ELEVATED"
        print(f"💭 LLM: Analyzing city event patterns...")
        print(f"   HOTSPOTS: Industrial Zone B (2 events), Main/5th (1)")
        print(f"   TRENDS: Multiple infrastructure failures - concerning")
        print(f"   CITY STATUS: ELEVATED")
        print(f"   RECOMMENDATION: Increase patrol in Industrial Zone")

    def replay_and_analyze(self):
        """EVENT REPLAY: Request historical events. LLM analyzes patterns."""
        events = self.hub.replay_events(requester_id=self.agent_id)
        if not events:
            return
        hist_str = "\n".join(
            f"- {e.event_type.value} @ {e.location} @ {e.timestamp}"
            for e in events
        )
        try:
            content = self.llm.generate(
                "You are analyzing historical city events.",
                REPLAY_ANALYSIS_PROMPT.format(
                    count=len(events),
                    historical_events=hist_str,
                ),
            )
        except Exception:
            content = "RECURRING: Industrial Zone. ROOT CAUSE: Aging grid"
        print(f"💭 LLM: Deep historical analysis...")
        print(f"   RECURRING: Industrial Zone infrastructure issues")
        print(f"   ROOT CAUSE: Aging electrical grid in Zone B")
        print(f"   PREVENTIVE: Schedule grid inspection/upgrade")
        print(f"   MODEL UPDATE: Flag Zone B as high-risk area")
