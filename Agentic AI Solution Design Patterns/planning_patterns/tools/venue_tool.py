"""Simulated venue search tool."""


def search_venues(
    capacity: int,
    dates: list[str],
    venue_type: str = "engaging",
) -> dict:
    return {
        "venues": [
            {
                "name": "Innovation Hub",
                "capacity": 25,
                "price": 800,
                "available": ["15th", "18th"],
                "activities": ["workshop", "brainstorm"],
            },
            {
                "name": "Creative Space",
                "capacity": 20,
                "price": 600,
                "available": ["18th", "22nd"],
                "activities": ["team-building", "design sprint"],
            },
        ],
        "capacity": capacity,
        "dates": dates,
    }
