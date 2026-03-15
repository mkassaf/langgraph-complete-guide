"""Simulated document creation tool."""


def create_proposal(details: dict) -> dict:
    return {
        "file": "meeting_proposal.pdf",
        "status": "created",
        "pages": 3,
        "details": details,
    }
