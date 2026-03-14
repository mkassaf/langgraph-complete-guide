"""
ReAct Tools — Venue Search Tool

Simulates searching for meeting venues.
"""

from tools.base_tool import BaseTool, ToolResult


class VenueSearchTool(BaseTool):
    """
    Simulates searching for meeting venues.
    """

    name = "venue_search_tool"

    VENUES = [
        {
            "name": "The Innovation Hub",
            "capacity": 30,
            "type": "engaging",
            "features": ["breakout rooms", "outdoor space", "AV equipment"],
            "price_per_day": 800,
            "available_dates": ["15th", "18th", "22nd"],
        },
        {
            "name": "Creative Space Co",
            "capacity": 20,
            "type": "engaging",
            "features": ["workshop area", "rooftop", "catering kitchen"],
            "price_per_day": 600,
            "available_dates": ["18th", "20th"],
        },
        {
            "name": "Standard Conference Center",
            "capacity": 50,
            "type": "standard",
            "features": ["projector", "whiteboard"],
            "price_per_day": 400,
            "available_dates": ["14th", "18th", "22nd", "25th"],
        },
    ]

    def execute(
        self,
        capacity: int = 15,
        dates: list | None = None,
        type: str = "engaging",
        **kwargs,
    ) -> ToolResult:
        """Filter venues by capacity, dates, and type."""
        dates = dates or ["18th", "22nd"]
        if isinstance(dates, str):
            dates = [dates]

        matches = []
        for v in self.VENUES:
            if v["capacity"] >= capacity and v["type"] == type:
                avail = [d for d in dates if d in v["available_dates"]]
                if avail:
                    matches.append({**v, "available_on_requested": avail})

        if not matches:
            matches = [v for v in self.VENUES if v["capacity"] >= capacity]

        lines = []
        for v in matches[:5]:
            lines.append(
                f"- {v['name']}: capacity {v['capacity']}, ${v['price_per_day']}/day, "
                f"features: {', '.join(v['features'])}"
            )

        observation = (
            "Available venues:\n" + "\n".join(lines)
            if lines
            else "No venues match criteria. Try relaxing capacity or type."
        )

        return ToolResult(
            tool_name=self.name,
            success=bool(matches),
            data={"venues": matches},
            observation=observation,
        )
