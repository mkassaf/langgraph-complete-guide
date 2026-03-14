"""
Maintenance Agent — subscribes to events.
"""

from fabric.messaging_fabric import MessagingFabric
from platforms.event_hub import Event
from prompts import MAINTENANCE_RESPONSE_PROMPT


class MaintenanceAgent:
    """
    Responds to maintenance needs.
    Subscribes to: overheat, abnormal_vibration, machine_failure
    """

    agent_id = "maintenance_agent"

    def __init__(self, llm_client):
        self.llm = llm_client

    def handle_safety_events(self, fabric: MessagingFabric) -> list[dict]:
        """Receive safety events from hub. LLM determines response."""
        results = []
        while True:
            event = fabric.consume_event(self.agent_id)
            if not event:
                break
            try:
                content = self.llm.generate(
                    "You are a maintenance agent.",
                    MAINTENANCE_RESPONSE_PROMPT.format(event=str(event.payload)),
                )
            except Exception:
                content = "URGENCY: immediate. MAINTENANCE_TASK: Inspect and cool down."
            results.append({"event": event.event_type, "response": content[:200]})
        return results
