"""
Tool Spec — Specification for a tool in the registry.
"""

from dataclasses import dataclass


@dataclass
class ToolSpec:
    """
    Complete specification for a tool in the registry.
    """

    id: str
    name: str
    category: str  # "booking"|"IT"|"facilities"|"admin"|"security"|"catering"
    description: str
    use_cases: list[str]
    parameters: dict
    returns: str
    example_usage: str
    permissions_required: list[str]

    def to_short_description(self) -> str:
        """Compact version for initial discovery response."""
        desc = self.description[:100] + "..." if len(self.description) > 100 else self.description
        return f"{self.name}: {desc}"

    def to_full_spec(self) -> str:
        """Full spec including params and examples."""
        params = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"{self.name}({params})\n  {self.description}\n  Example: {self.example_usage}"
