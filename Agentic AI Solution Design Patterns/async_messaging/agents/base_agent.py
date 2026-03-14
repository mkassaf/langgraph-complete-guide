"""
Base agent for async messaging architecture.
"""


class BaseAgent:
    """Base class for order processing agents."""

    agent_id: str = "base_agent"

    def __init__(self, llm_client):
        self.llm = llm_client
