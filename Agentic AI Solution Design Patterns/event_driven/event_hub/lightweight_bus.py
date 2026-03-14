"""
Lightweight in-memory event bus for INTRA-AGENT use.
"""

from typing import Callable


class LightweightEventBus:
    """
    Lightweight in-memory event bus for INTRA-AGENT use.

    From lesson: 'For this purpose, there are lightweight
    Event Hub products available, such as in-memory event
    buses and queues, and embedded message brokers with
    publish and subscribe features.'

    Used WITHIN a single agent between its microservices.
    No persistence. Just fast in-memory pub-sub.
    """

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event_type: str, handler: Callable):
        """Register handler for internal event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(handler)

    def emit(self, event_type: str, data: dict):
        """
        Emit internal event - triggers all handlers immediately.
        """
        handlers = self._listeners.get(event_type, [])
        print(f"[INTERNAL BUS] {event_type} emitted")
        print(f"           → triggering {len(handlers)} handlers")
        for handler in handlers:
            handler(data)
