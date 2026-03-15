"""Simulated booking tool (fast - ~1.8s, can skip venue_search for known venues)."""


def book_venue(venue_name: str, date: str, guests: int) -> dict:
    return {
        "status": "confirmed",
        "venue": venue_name,
        "date": date,
        "guests": guests,
        "confirmation_id": "BKG-001",
    }
