"""
Student activity data for learning platform.
"""

STUDENT_ACTIVITIES = [
    {
        "student_id": "STU-001",
        "name": "Ahmed Al-Rashid",
        "activity_type": "quiz_completed",
        "topic": "Python Functions",
        "score": 40,
        "time_spent_minutes": 8,
        "previous_scores": [75, 82, 68],
    },
    {
        "student_id": "STU-001",
        "activity_type": "lesson_struggled",
        "topic": "Object-Oriented Programming Basics",
        "time_spent_minutes": 30,
        "completion": False,
        "replays": 4,
    },
    {
        "student_id": "STU-002",
        "name": "Sara Mohammed",
        "activity_type": "quiz_completed",
        "topic": "Data Structures",
        "score": 35,
        "time_spent_minutes": 15,
        "previous_scores": [90, 88, 92],
    },
]

THRESHOLDS = {
    "low_quiz_score": 60,
    "struggle_time_minutes": 20,
    "topic_replays": 3,
}
