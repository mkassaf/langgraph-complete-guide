"""
City Monitor Agent — PRODUCER: detects city events via sensors.
"""

from event_hub import EventHub, CityEvent, EventType, EventSeverity, LightweightEventBus
from prompts import CITY_MONITOR_PROMPT


class CityMonitorAgent:
    """
    PRODUCER agent - detects city events via sensors.

    From lesson: 'When a producer agent detects a noteworthy
    event, it sends or publishes the event to the Event Hub.
    The producer agent doesn't send a message to any specific
    consumer agent, nor does it wait for any agent to
    immediately process the event.'

    Contains internal lightweight bus showing intra-agent
    event-driven architecture.
    """

    agent_id = "city_monitor_agent"

    SENSOR_DATA = [
        {
            "sensor_id": "TRF-001",
            "location": "Main Street & 5th Ave",
            "reading": {"speed_kmh": 8, "density": "extreme"},
            "event_type": EventType.TRAFFIC_JAM,
        },
        {
            "sensor_id": "FIRE-007",
            "location": "Industrial Zone B",
            "reading": {"temp_celsius": 450, "smoke_level": "critical"},
            "event_type": EventType.FIRE_DETECTED,
        },
        {
            "sensor_id": "PWR-023",
            "location": "Residential District 4",
            "reading": {"voltage": 0, "affected_homes": 847},
            "event_type": EventType.POWER_OUTAGE,
        },
        {
            "sensor_id": "AIR-012",
            "location": "City Center",
            "reading": {"aqi": 187, "pm25": 95},
            "event_type": EventType.AIR_QUALITY_ALERT,
        },
        {
            "sensor_id": "TRF-008",
            "location": "Highway 101 North",
            "reading": {"accident": True, "lanes_blocked": 2},
            "event_type": EventType.ACCIDENT,
        },
    ]

    def __init__(self, llm_client, event_hub: EventHub):
        self.llm = llm_client
        self.hub = event_hub
        self.internal_bus = LightweightEventBus()
        self._setup_internal_handlers()

    def _setup_internal_handlers(self):
        """Setup intra-agent event handlers."""
        def analysis_handler(data):
            print(f"  → analysis_microservice: processing sensor {data.get('sensor_id', '')}")

        def alert_handler(data):
            print(f"  → alert_microservice: flagging {data.get('anomaly_type', 'anomaly')}")

        def classification_handler(data):
            print(f"  → classification_microservice: classifying as {data.get('event_type', '')}")

        self.internal_bus.on("sensor_reading", analysis_handler)
        self.internal_bus.on("anomaly_detected", alert_handler)
        self.internal_bus.on("anomaly_detected", classification_handler)

    def monitor_and_publish(self):
        """
        For each sensor reading:
        1. Emit to INTERNAL bus
        2. LLM determines if noteworthy
        3. Publish to EXTERNAL Event Hub
        4. Continue to next sensor (don't wait!)
        """
        for sensor in self.SENSOR_DATA:
            self.internal_bus.emit("sensor_reading", sensor)
            try:
                content = self.llm.generate(
                    "You are a city monitoring agent.",
                    CITY_MONITOR_PROMPT.format(sensor_data=str(sensor)),
                )
            except Exception:
                content = "IS_NOTEWORTHY: yes. PUBLISH_TO_HUB: yes"
            if "publish_to_hub: no" in content.lower():
                continue
            severity = EventSeverity.CRITICAL if "critical" in content.lower() else EventSeverity.WARNING
            if sensor["event_type"] == EventType.FIRE_DETECTED:
                severity = EventSeverity.CRITICAL
            desc = content[:100] if len(content) > 50 else f"Sensor {sensor['sensor_id']} anomaly"
            self.internal_bus.emit(
                "anomaly_detected",
                {"anomaly_type": sensor["event_type"].value, "event_type": sensor["event_type"].value},
            )
            print(f"💭 LLM: Sensor {sensor['sensor_id']} shows {sensor['event_type'].value} - noteworthy")
            event = CityEvent(
                event_type=sensor["event_type"],
                severity=severity,
                publisher_id=self.agent_id,
                location=sensor["location"],
                description=desc,
                data=sensor["reading"],
            )
            self.hub.publish(event)
            print(f"city_monitor_agent continues to next sensor ✓")
