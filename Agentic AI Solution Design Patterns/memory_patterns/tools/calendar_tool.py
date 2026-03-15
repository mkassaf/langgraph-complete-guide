"""Simulated calendar tool."""


def check_availability(team_size: int, weeks_ahead: int = 3) -> dict:
    return {
        "available_dates": ["15th", "18th", "22nd"],
        "blocked_dates": ["10th", "20th"],
        "team_size": team_size,
    }
