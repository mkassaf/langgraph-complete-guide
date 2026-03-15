"""Simulated catering tool."""

APPROVED_VENDORS = ["Fresh & Local", "Quick Bites", "Corporate Catering"]


def get_catering(guests: int, venue: str, date: str) -> dict:
    return {
        "options": [
            {"provider": "Fresh & Local", "per_person": 45, "total": guests * 45},
            {"provider": "Quick Bites", "per_person": 30, "total": guests * 30},
        ],
        "guests": guests,
        "venue": venue,
        "date": date,
    }
