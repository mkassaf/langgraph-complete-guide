"""Catering tool."""

from tools.base_tool import BaseTool, ToolResult


class CateringTool(BaseTool):
    name = "catering_tool"
    CATERERS = [
        {"name": "Fresh & Local", "min_guests": 10, "max_guests": 50, "price_per_person": 45, "menu_options": ["Mediterranean", "Asian Fusion"]},
        {"name": "Quick Bites Pro", "min_guests": 5, "max_guests": 25, "price_per_person": 30, "menu_options": ["Sandwiches", "Salads"]},
    ]

    def execute(self, guests=15, venue="", date="", **kwargs) -> ToolResult:
        options = [c for c in self.CATERERS if c["min_guests"] <= guests <= c["max_guests"]]
        lines = [f"- {c['name']}: ${c['price_per_person']}/person" for c in options]
        observation = "Catering options:\n" + "\n".join(lines) if lines else "No caterers available."
        return ToolResult(tool_name=self.name, success=bool(options), data={"options": options}, observation=observation)
