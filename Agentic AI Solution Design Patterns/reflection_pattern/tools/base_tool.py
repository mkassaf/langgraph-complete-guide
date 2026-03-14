"""Base tool class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    data: dict
    observation: str


class BaseTool(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass
