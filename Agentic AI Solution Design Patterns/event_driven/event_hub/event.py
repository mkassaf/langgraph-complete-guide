"""
Event data structures for Event-Driven Architecture.
"""

from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class EventType(Enum):
    TRAFFIC_JAM = "traffic_jam"
    ACCIDENT = "accident"
    ROAD_CLOSURE = "road_closure"
    FIRE_DETECTED = "fire_detected"
    MEDICAL_EMERGENCY = "medical_emergency"
    CRIME_REPORTED = "crime_reported"
    POWER_OUTAGE = "power_outage"
    WATER_LEAK = "water_leak"
    STREETLIGHT_FAILURE = "streetlight_failure"
    AIR_QUALITY_ALERT = "air_quality_alert"
    FLOOD_WARNING = "flood_warning"
    NOISE_VIOLATION = "noise_violation"


class EventSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class CityEvent:
    """
    Event published to the Event Hub.

    Key difference from async messaging:
    - No recipient_id (not sent to anyone specific)
    - Producer declares WHAT HAPPENED
    - Any subscribed consumer can react
    """

    event_id: str = field(
        default_factory=lambda: f"EVT-{str(uuid.uuid4())[:6].upper()}"
    )
    event_type: EventType = EventType.TRAFFIC_JAM
    severity: EventSeverity = EventSeverity.INFO
    publisher_id: str = ""
    location: str = ""
    description: str = ""
    data: dict = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%H:%M:%S")
    )
