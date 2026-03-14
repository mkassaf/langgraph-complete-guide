"""
Base agent for warehouse fulfillment.
"""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for warehouse agents."""

    agent_id: str = ""
    agent_type: str = ""

    def __init__(self, llm_client, private_memory, shared_memory=None):
        self.llm = llm_client
        self.private_memory = private_memory
        self.shared_memory = shared_memory

    @abstractmethod
    def execute(self, task: dict) -> dict:
        """Execute agent task."""
        ...
