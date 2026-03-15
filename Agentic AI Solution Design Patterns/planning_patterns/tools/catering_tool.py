"""Simulated catering tool."""


def get_catering(guests: int, venue: str, date: str) -> dict:
    return {
        "options": [
            {
                "provider": "Fresh & Local",
                "per_person": 45,
                "total": guests * 45,
                "menu": "Mediterranean",
            },
            {
                "provider": "Quick Bites",
                "per_person": 30,
                "total": guests * 30,
                "menu": "International",
            },
        ],
        "guests": guests,
        "venue": venue,
        "date": date,
    }
