"""
Content library for learning platform.
"""

CONTENT_LIBRARY = {
    "Python Functions": {
        "remedial_videos": [
            {"id": "VID-101", "title": "Functions Basics - Visual Guide", "duration_min": 8, "difficulty": "beginner"},
            {"id": "VID-102", "title": "Function Parameters Deep Dive", "duration_min": 12, "difficulty": "intermediate"},
        ],
        "practice_exercises": [
            {"id": "EX-201", "title": "Simple Function Builder", "estimated_min": 15, "difficulty": "beginner"},
            {"id": "EX-202", "title": "Function Challenges", "estimated_min": 20, "difficulty": "intermediate"},
        ],
        "articles": [
            {"id": "ART-301", "title": "Understanding Python Functions", "reading_min": 5},
        ],
    },
    "Object-Oriented Programming Basics": {
        "remedial_videos": [
            {"id": "VID-111", "title": "OOP Explained Simply", "duration_min": 10, "difficulty": "beginner"},
            {"id": "VID-112", "title": "Classes and Objects Visualization", "duration_min": 15, "difficulty": "beginner"},
        ],
        "practice_exercises": [
            {"id": "EX-211", "title": "Build Your First Class", "estimated_min": 20, "difficulty": "beginner"},
        ],
        "articles": [
            {"id": "ART-311", "title": "OOP Concepts Made Easy", "reading_min": 7},
        ],
    },
    "Data Structures": {
        "remedial_videos": [
            {"id": "VID-121", "title": "Data Structures Overview", "duration_min": 12, "difficulty": "beginner"},
        ],
        "practice_exercises": [
            {"id": "EX-221", "title": "Lists and Dictionaries Practice", "estimated_min": 25, "difficulty": "intermediate"},
        ],
        "articles": [
            {"id": "ART-321", "title": "Choosing the Right Data Structure", "reading_min": 6},
        ],
    },
}

PEER_BENCHMARKS = {
    "Python Functions": {"avg_score": 74, "avg_time_min": 9},
    "Object-Oriented Programming Basics": {"avg_score": 68, "avg_time_min": 22},
    "Data Structures": {"avg_score": 71, "avg_time_min": 13},
}
