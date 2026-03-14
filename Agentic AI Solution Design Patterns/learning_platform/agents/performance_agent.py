"""
Performance Analysis Agent — CONSUMER ① → PRODUCER ②
"""

import json

from event_hub import LearningEventHub, LearningEvent, LearningEventType
from prompts import PERFORMANCE_ANALYSIS_PROMPT


class PerformanceAnalysisAgent:
    """
    AGENT 2: Performance Analysis Agent
    CONSUMER ① → PRODUCER ②

    From lesson: 'It compares the student's performance
    against learning objectives, peer benchmarks, and
    historical data. It does this to analyze strengths
    and weaknesses and potential knowledge gaps.'

    Subscribed to: LEARNING_INTERACTION ①
    Publishes: SKILL_GAP_DETECTED ②
    """

    def __init__(self, llm_client, hub: LearningEventHub):
        self.llm = llm_client
        self.hub = hub
        self.hub.subscribe(
            "performance_agent",
            [LearningEventType.LEARNING_INTERACTION],
        )

    def poll_and_analyze(
        self,
        all_activities: list,
        peer_benchmarks: dict,
    ) -> list[LearningEvent]:
        """Poll for LEARNING_INTERACTION events, analyze, publish SKILL_GAP_DETECTED."""
        events = self.hub.get_events("performance_agent")
        for ev in events:
            print("📈 performance_agent received EVENT ①")
            student_activities = [
                a for a in all_activities if a.get("student_id") == ev.student_id
            ]
            topic = ev.payload.get("activity", {}).get("topic", "")
            benchmarks = peer_benchmarks.get(topic, {})
            prompt = PERFORMANCE_ANALYSIS_PROMPT.format(
                event=json.dumps(ev.payload, indent=2),
                student_data=json.dumps(student_activities, indent=2),
                benchmarks=json.dumps(benchmarks, indent=2),
            )
            response = self.llm.generate(
                system_prompt="You analyze student performance and identify skill gaps.",
                user_message=prompt,
            )
            skill_event = LearningEvent(
                event_type=LearningEventType.SKILL_GAP_DETECTED,
                publisher_id="performance_agent",
                student_id=ev.student_id,
                payload={
                    "original_event": ev.payload,
                    "analysis": response,
                },
                event_number="②",
            )
            self.hub.publish(skill_event)
        return events
