"""Simulated venue search tool (slow - ~9s)."""


def search_venues(capacity: int, dates: list[str]) -> dict:
    return {
        "venues": [
            {"name": "Innovation Suite", "capacity": 25, "price": 800},
            {"name": "Creative Space", "capacity": 20, "price": 600},
        ],
        "capacity": capacity,
        "dates": dates,
    }
