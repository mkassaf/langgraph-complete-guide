"""
Episodic memory — user interaction records.

From lesson: 'data about events, like specific past interactions
with users or other agents'
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class EpisodicRecord:
    """A record of a past user interaction/event."""

    record_id: str
    user_id: str
    request: str
    outcome: str
    user_preferences: dict
    feedback: str
    timestamp: str


class EpisodicStore:
    def create_record(self, session_data: dict) -> EpisodicRecord:
        """Package user-facing session data into episodic record."""
        prefs = self.extract_preferences(session_data)
        return EpisodicRecord(
            record_id=session_data.get("record_id", f"EP-{datetime.now().strftime('%H%M%S')}"),
            user_id=session_data.get("user", "unknown"),
            request=session_data.get("request", ""),
            outcome=session_data.get("outcome", "success"),
            user_preferences=prefs,
            feedback=session_data.get("user_feedback", ""),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

    def extract_preferences(self, session_data: dict) -> dict:
        """Extract user preferences from session."""
        prefs = {}
        if session_data.get("venue_chosen"):
            prefs["venue"] = session_data["venue_chosen"]
        if session_data.get("catering"):
            prefs["catering"] = session_data["catering"]
        return prefs
