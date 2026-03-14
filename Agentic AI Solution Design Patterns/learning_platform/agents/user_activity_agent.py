"""
User Activity Agent — PRODUCER only.
"""

import json

from event_hub import LearningEventHub, LearningEvent, LearningEventType
from prompts import ACTIVITY_MONITOR_PROMPT


class UserActivityAgent:
    """
    AGENT 1: User Activity Agent - PRODUCER only

    From lesson: 'continuously monitors a student's
    interactions within the platform, like when the
    student completes lessons, the time they spend on
    individual topics, what they search for, and the
    scores that they get in quizzes.'

    'By doing this, the user activity agent simply
    registers what happened. It doesn't know or care
    how other agents might react.'

    Subscribed to: NOTHING (pure producer)
    Publishes: LEARNING_INTERACTION events ①
    """

    def __init__(self, llm_client, hub: LearningEventHub):
        self.llm = llm_client
        self.hub = hub

    def monitor_student_activity(self, activity: dict, thresholds: dict) -> bool:
        """
        LLM assesses if activity is a significant event.
        If yes, publish to Event Hub.
        """
        prompt = ACTIVITY_MONITOR_PROMPT.format(
            activity=json.dumps(activity, indent=2),
            low_score_threshold=thresholds.get("low_quiz_score", 60),
            struggle_time=thresholds.get("struggle_time_minutes", 20),
            replay_threshold=thresholds.get("topic_replays", 3),
        )
        response = self.llm.generate(
            system_prompt="You assess student activities. Reply with structured fields.",
            user_message=prompt,
        )
        parts = response.upper().split("PUBLISH_EVENT:")
        tail = parts[-1].strip().split() if len(parts) > 1 and parts[-1].strip() else []
        publish = tail and "YES" in tail[0]
        if publish:
            event = LearningEvent(
                event_type=LearningEventType.LEARNING_INTERACTION,
                publisher_id="user_activity_agent",
                student_id=activity.get("student_id", ""),
                payload={
                    "activity": activity,
                    "llm_reason": response[:200],
                },
                event_number="①",
            )
            self.hub.publish(event)
            return True
        return False
