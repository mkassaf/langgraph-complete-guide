"""
Adaptive Interface Agent — CONSUMER ② AND ③
"""

import json

from event_hub import LearningEventHub, LearningEvent, LearningEventType
from prompts import INTERFACE_SKILL_GAP_PROMPT, INTERFACE_RECOMMENDATIONS_PROMPT


class AdaptiveInterfaceAgent:
    """
    AGENT 4: Adaptive Interface Agent
    CONSUMER ② AND ③ (subscribed to TWO events!)

    From lesson:
    'When it receives the skill_gap_detected event,
    it might react by adjusting the user's dashboard
    to highlight relevant sections or provide quick
    access to helpful resources.'

    'The adaptive interface agent is also subscribed
    to the recommendations ready event. When it sees
    this event, it updates the user's personalized
    learning dashboard with the new content suggestions.'

    Subscribed to: SKILL_GAP_DETECTED ② AND RECOMMENDATION_READY ③
    Publishes: NOTHING (end of chain)
    """

    def __init__(self, llm_client, hub: LearningEventHub):
        self.llm = llm_client
        self.hub = hub
        self.hub.subscribe(
            "interface_agent",
            [
                LearningEventType.SKILL_GAP_DETECTED,
                LearningEventType.RECOMMENDATION_READY,
            ],
        )
        self.dashboard_state: dict[str, dict] = {}

    def poll_and_adapt(self) -> int:
        """Poll for both event types and react differently to each."""
        events = self.hub.get_events("interface_agent")
        for ev in events:
            if ev.event_type == LearningEventType.SKILL_GAP_DETECTED:
                print("🖥️  interface_agent received EVENT ② (FIRST reaction)")
                self._react_to_skill_gap(ev)
            else:
                print("🖥️  interface_agent received EVENT ③ (SECOND reaction)")
                self._react_to_recommendations(ev)
        return len(events)

    def _react_to_skill_gap(self, event: LearningEvent):
        """Immediate dashboard adjustment for skill gap."""
        prompt = INTERFACE_SKILL_GAP_PROMPT.format(
            skill_gap_event=json.dumps(event.payload, indent=2),
        )
        response = self.llm.generate(
            system_prompt="You adjust the student dashboard for skill gaps.",
            user_message=prompt,
        )
        sid = event.student_id
        if sid not in self.dashboard_state:
            self.dashboard_state[sid] = {}
        self.dashboard_state[sid]["skill_gap_reaction"] = response

    def _react_to_recommendations(self, event: LearningEvent):
        """Add recommendations to personalized dashboard."""
        prompt = INTERFACE_RECOMMENDATIONS_PROMPT.format(
            recommendations_event=json.dumps(event.payload, indent=2),
        )
        response = self.llm.generate(
            system_prompt="You update the learning dashboard with recommendations.",
            user_message=prompt,
        )
        sid = event.student_id
        if sid not in self.dashboard_state:
            self.dashboard_state[sid] = {}
        self.dashboard_state[sid]["recommendations_reaction"] = response

    def show_student_dashboard(self, student_id: str) -> str:
        """Display current state of student's dashboard."""
        state = self.dashboard_state.get(student_id, {})
        return json.dumps(state, indent=2)
