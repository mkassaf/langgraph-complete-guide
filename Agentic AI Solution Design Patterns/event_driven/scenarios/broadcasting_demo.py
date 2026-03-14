"""
Broadcasting Demo — One event → many consumers.
"""

from event_hub import EventHub, CityEvent, EventType, EventSeverity


def run_broadcasting_demo(hub: EventHub):
    """Demonstrate FIRE_DETECTED reaching emergency + maintenance + analytics."""
    event = CityEvent(
        event_type=EventType.FIRE_DETECTED,
        severity=EventSeverity.CRITICAL,
        publisher_id="demo",
        location="Industrial Zone B",
        description="Fire detected",
    )
    n = hub.publish(event)
    return n
