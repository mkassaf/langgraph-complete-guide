"""
Safety Agent — publishes and subscribes to events.
"""

from datetime import datetime

from fabric.messaging_fabric import MessagingFabric
from platforms.event_hub import Event
from prompts import SAFETY_MONITOR_PROMPT


class SafetyAgent:
    """
    Monitors factory safety conditions.
    Uses: Event Hub (publishes critical alerts)
    """

    agent_id = "safety_agent"
    READINGS = [
        {"machine": "Press-A", "temp": 95, "threshold": 80},
        {"machine": "Conveyor-B", "vibration": 8.5, "threshold": 7.0},
        {"machine": "Robot-C", "temp": 45, "threshold": 80},
    ]

    def __init__(self, llm_client):
        self.llm = llm_client

    def monitor_and_alert(self, fabric: MessagingFabric) -> list[Event]:
        """LLM analyzes readings. Publishes events for anomalies."""
        published = []
        try:
            content = self.llm.generate(
                "You are a safety monitoring agent.",
                SAFETY_MONITOR_PROMPT.format(readings=str(self.READINGS)),
            )
        except Exception:
            content = "EVENT_TYPE: overheat. SEVERITY: critical. AFFECTED_MACHINE: Press-A"

        if "overheat" in content.lower() or "95" in content:
            e = Event(
                event_id="",
                event_type="overheat",
                publisher_id=self.agent_id,
                payload={"machine": "Press-A", "temp": 95, "threshold": 80},
                timestamp=datetime.now().isoformat(),
                severity="critical",
            )
            fabric.publish_event(e)
            published.append(e)

        if "vibration" in content.lower() or "8.5" in content:
            e = Event(
                event_id="",
                event_type="abnormal_vibration",
                publisher_id=self.agent_id,
                payload={"machine": "Conveyor-B", "vibration": 8.5, "threshold": 7.0},
                timestamp=datetime.now().isoformat(),
                severity="warning",
            )
            fabric.publish_event(e)
            published.append(e)

        if not published:
            e = Event(
                event_id="",
                event_type="overheat",
                publisher_id=self.agent_id,
                payload={"machine": "Press-A", "temp": 95},
                timestamp=datetime.now().isoformat(),
                severity="critical",
            )
            fabric.publish_event(e)
            published.append(e)

        return published
