"""Venue search tool."""

from tools.base_tool import BaseTool, ToolResult


class VenueSearchTool(BaseTool):
    name = "venue_search_tool"
    VENUES = [
        {"name": "The Innovation Hub", "capacity": 30, "type": "engaging", "features": ["breakout rooms", "outdoor space"], "price_per_day": 800, "available_dates": ["15th", "18th", "22nd"]},
        {"name": "Creative Space Co", "capacity": 20, "type": "engaging", "features": ["workshop area", "rooftop"], "price_per_day": 600, "available_dates": ["18th", "20th"]},
    ]

    def execute(self, capacity=15, dates=None, type="engaging", **kwargs) -> ToolResult:
        dates = dates or ["18th", "22nd"]
        if isinstance(dates, str):
            dates = [dates]
        matches = [v for v in self.VENUES if v["capacity"] >= capacity and v["type"] == type]
        lines = [f"- {v['name']}: ${v['price_per_day']}/day" for v in matches[:5]]
        observation = "Available venues:\n" + "\n".join(lines) if lines else "No venues match."
        return ToolResult(tool_name=self.name, success=bool(matches), data={"venues": matches}, observation=observation)
