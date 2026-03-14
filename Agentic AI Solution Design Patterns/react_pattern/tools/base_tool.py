"""
ReAct Tools — Base Tool Class

Abstract base for all ReAct tools.
Tools are the ACTION layer — what the agent uses to interact with the outside world.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result from tool execution."""
    tool_name: str
    success: bool
    data: dict
    observation: str  # Human-readable result fed back to LLM


class BaseTool(ABC):
    """
    Abstract base for all ReAct tools.
    Tools are the ACTION layer - what the agent uses
    to interact with the outside world.
    """

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool and return observation."""
