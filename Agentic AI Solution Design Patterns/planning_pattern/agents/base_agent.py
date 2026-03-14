"""
Base agent class for Planning pattern.
"""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    Base class for all agents in the Planning pattern.
    Both Orchestrator and Workers inherit from this.
    """

    agent_id: str = ""
    agent_type: str = ""  # "orchestrator" | "worker"

    @abstractmethod
    def process(self, input_data: dict) -> dict:
        """Process input and return result."""
        ...

    def get_status(self) -> dict:
        """Return current agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
        }
