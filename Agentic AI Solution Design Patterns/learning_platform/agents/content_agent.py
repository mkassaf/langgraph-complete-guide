"""
Content Recommendation Agent — CONSUMER ② → PRODUCER ③
"""

import json

from event_hub import LearningEventHub, LearningEvent, LearningEventType
from prompts import CONTENT_RECOMMENDATION_PROMPT


class ContentRecommendationAgent:
    """
    AGENT 3: Content Recommendation Agent
    CONSUMER ② → PRODUCER ③

    From lesson: 'it queries the system's library of
    courses, articles, videos, and practice exercises
    to find content that it can suggest to the student
    to help address the identified skill gap. Once it
    has assembled this content, it publishes a
    recommendation ready event back to the event hub.'

    Subscribed to: SKILL_GAP_DETECTED ②
    Publishes: RECOMMENDATION_READY ③
    """

    def __init__(self, llm_client, hub: LearningEventHub):
        self.llm = llm_client
        self.hub = hub
        self.hub.subscribe(
            "content_agent",
            [LearningEventType.SKILL_GAP_DETECTED],
        )

    def poll_and_recommend(self, content_library: dict) -> list[LearningEvent]:
        """Poll for SKILL_GAP_DETECTED events, select content, publish RECOMMENDATION_READY."""
        events = self.hub.get_events("content_agent")
        for ev in events:
            print("📚 content_agent received EVENT ②")
            orig = ev.payload.get("original_event", {})
            topic = orig.get("activity", orig).get("topic", "")
            available = content_library.get(topic, content_library)
            prompt = CONTENT_RECOMMENDATION_PROMPT.format(
                skill_gap_event=json.dumps(ev.payload, indent=2),
                available_content=json.dumps(available, indent=2),
            )
            response = self.llm.generate(
                system_prompt="You select the best learning content for skill gaps.",
                user_message=prompt,
            )
            rec_event = LearningEvent(
                event_type=LearningEventType.RECOMMENDATION_READY,
                publisher_id="content_agent",
                student_id=ev.student_id,
                payload={
                    "skill_gap_event": ev.payload,
                    "recommendations": response,
                },
                event_number="③",
            )
            self.hub.publish(rec_event)
        return events
