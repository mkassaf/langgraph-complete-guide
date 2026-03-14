"""
Central Event Hub for learning platform.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class LearningEventType(Enum):
    LEARNING_INTERACTION = "learning_interaction"  # ①
    SKILL_GAP_DETECTED = "skill_gap_detected"  # ②
    RECOMMENDATION_READY = "recommendation_ready"  # ③


@dataclass
class LearningEvent:
    """
    Event flowing through the learning platform hub.
    NO recipient - any subscribed agent reacts.
    """

    event_id: str = field(default_factory=lambda: f"EVT-{str(uuid.uuid4())[:6].upper()}")
    event_type: LearningEventType = LearningEventType.LEARNING_INTERACTION
    publisher_id: str = ""
    student_id: str = ""
    payload: dict = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%H:%M:%S")
    )
    event_number: str = ""  # ① ② ③ for display


class LearningEventHub:
    """
    Central Event Hub for the learning platform.

    From lesson: 'all driven by the flow of events through
    the central hub without direct agent-to-agent communication'

    Key: Producer has NO knowledge of who reacts.
    All reactions are triggered by events, not direct calls.
    """

    def __init__(self):
        self._subscriptions: dict[LearningEventType, list[str]] = {
            et: [] for et in LearningEventType
        }
        self._event_stream: list[LearningEvent] = []
        self._pending: dict[str, list[LearningEvent]] = {}
        self.delivery_log: list[dict] = []

    def subscribe(self, agent_id: str, event_types: list[LearningEventType]):
        """Agent subscribes to event types."""
        for et in event_types:
            if agent_id not in self._subscriptions[et]:
                self._subscriptions[et].append(agent_id)
        types_str = ", ".join(e.value for e in event_types)
        print(f"[EVENT HUB] {agent_id} subscribed to: {types_str}")

    def publish(self, event: LearningEvent) -> int:
        """Agent publishes event. Delivers to ALL subscribers."""
        self._event_stream.append(event)
        notified = self._subscriptions.get(event.event_type, [])
        for agent_id in notified:
            if agent_id not in self._pending:
                self._pending[agent_id] = []
            self._pending[agent_id].append(event)
            self.delivery_log.append(
                {"event_id": event.event_id, "subscriber": agent_id}
            )
        print(f"══════════════════════════════════════════════")
        print(f"🔔 [EVENT HUB] Event Published  ← EVENT {event.event_number}")
        print(f"   Type:      {event.event_type.value}")
        print(f"   Publisher: {event.publisher_id}")
        print(f"              (no knowledge of who reacts)")
        print(f"   Student:   {event.student_id}")
        if event.payload:
            for k, v in list(event.payload.items())[:3]:
                print(f"   {k}: {str(v)[:50]}")
        print(f"   → Delivered to {len(notified)} agents: {notified}")
        print(f"══════════════════════════════════════════════")
        return len(notified)

    def get_events(self, agent_id: str) -> list[LearningEvent]:
        """Agent polls for pending events."""
        events = self._pending.get(agent_id, [])
        self._pending[agent_id] = []
        return events

    def get_event_chain(self, student_id: str) -> list[LearningEvent]:
        """Get all events for a student's session."""
        return [e for e in self._event_stream if e.student_id == student_id]
