"""Simulated catering tool."""


def get_catering(guests: int, venue: str, preference: str = "") -> dict:
    options = [
        {"provider": "Fresh & Local", "menu": "Mediterranean", "per_person": 45},
        {"provider": "Quick Bites", "menu": "International", "per_person": 30},
    ]
    if "vegetarian" in preference.lower():
        options = [{"provider": "Fresh & Local", "menu": "Vegetarian Mediterranean", "per_person": 45}]
    return {
        "options": options,
        "guests": guests,
        "venue": venue,
        "preference": preference,
    }
