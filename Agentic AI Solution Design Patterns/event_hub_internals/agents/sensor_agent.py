"""
Sensor Agent — PRODUCER: publishes factory events.
"""

from platform import EventHubPlatform, EventChannel
from prompts import SENSOR_ASSESSMENT_PROMPT


class SensorAgent:
    """
    PRODUCER agent - publishes factory events.
    Shows EventReceiver in action.
    """

    agent_id = "sensor_agent"

    FACTORY_EVENTS = [
        {
            "type": "machine_overheat",
            "location": "Press-A",
            "data": {"temp": 95, "threshold": 80},
        },
        {
            "type": "safety_guard_removed",
            "location": "Robot-B",
            "data": {"guard_id": "GRD-007", "area": "zone_3"},
        },
        {
            "type": "quality_defect_detected",
            "location": "QC-Station-2",
            "data": {"defect_rate": 0.12, "threshold": 0.05},
        },
        {
            "type": "machine_vibration_anomaly",
            "location": "Conveyor-C",
            "data": {"vibration": 8.5, "normal": 3.0},
        },
    ]

    def __init__(self, llm_client, platform: EventHubPlatform):
        self.llm = llm_client
        self.platform = platform

    def publish_events(self, platform: EventHubPlatform):
        """LLM assesses each reading. Publishes noteworthy events."""
        for reading in self.FACTORY_EVENTS:
            try:
                content = self.llm.generate(
                    "You are a factory sensor monitoring agent.",
                    SENSOR_ASSESSMENT_PROMPT.format(reading=reading),
                )
            except Exception:
                content = "IS_NOTEWORTHY: yes. PUBLISH: yes"
            if "publish: no" in content.lower():
                continue
            print(f"💭 LLM: {reading['type']} at {reading['location']} - noteworthy!")
            platform.publish(
                self.agent_id,
                reading["type"],
                {"location": reading["location"], **reading["data"]},
            )
