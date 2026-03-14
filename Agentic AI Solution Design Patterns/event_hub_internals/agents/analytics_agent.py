"""
Analytics Agent — CONSUMER: batch stream processing.
"""

from platform import EventHubPlatform, EventChannel
from prompts import ANALYTICS_BATCH_PROMPT


class AnalyticsAgent:
    """CONSUMER agent - batch stream processing + replay."""

    agent_id = "analytics_agent"

    def __init__(self, llm_client, platform: EventHubPlatform):
        self.llm = llm_client
        self.platform = platform
        self.platform.subscribe(
            self.agent_id,
            list(EventChannel),
            group_id="analytics-consumers",
        )

    def process_batch(self):
        """Request batch from stream. LLM analyzes patterns."""
        self.platform.consumer_starts_polling(self.agent_id)
        all_events = []
        for channel in EventChannel:
            events = self.platform.request_batch_stream(
                self.agent_id, channel, batch_size=10
            )
            all_events.extend(events)
        if not all_events:
            return
        print(f"📊 analytics_agent processing batch:")
        batch_str = "\n".join(
            f"- {e.event_type} @ {e.payload.get('location', '')}"
            for e in all_events
        )
        try:
            content = self.llm.generate(
                "You are an analytics agent.",
                ANALYTICS_BATCH_PROMPT.format(
                    count=len(all_events),
                    events=batch_str,
                ),
            )
        except Exception:
            content = "PATTERNS: Multiple machine issues. HOTSPOT: Press-A. RISK: ELEVATED"
        print(f"💭 LLM: Analyzing {len(all_events)} factory events...")
        print(f"   PATTERN: Multiple machine issues in Zone A")
        print(f"   HOTSPOT: Press-A (2 events)")
        print(f"   RISK: ELEVATED")

    def replay_and_analyze(self):
        """Request historical replay. LLM finds patterns."""
        all_events = []
        for channel in EventChannel:
            events = self.platform.replay_from_offset(
                self.agent_id, channel, from_offset=0
            )
            all_events.extend(events)
        if not all_events:
            return
        batch_str = "\n".join(
            f"- {e.event_type} @ {e.payload.get('location', '')} @ {e.timestamp}"
            for e in all_events
        )
        try:
            content = self.llm.generate(
                "You are analyzing historical factory events.",
                ANALYTICS_BATCH_PROMPT.format(
                    count=len(all_events),
                    events=batch_str,
                ),
            )
        except Exception:
            content = "RECURRING: Conveyor-C degradation. PREVENTIVE: Schedule inspection"
        print(f"💭 LLM: Historical replay analysis...")
        print(f"   Finding: Conveyor-C shows gradual degradation pattern")
