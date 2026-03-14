"""
ReAct Tools — Catering Tool

Simulates getting catering options for an event.
"""

from tools.base_tool import BaseTool, ToolResult


class CateringTool(BaseTool):
    """
    Simulates getting catering options for an event.
    """

    name = "catering_tool"

    CATERERS = [
        {
            "name": "Fresh & Local",
            "min_guests": 10,
            "max_guests": 50,
            "price_per_person": 45,
            "menu_options": ["Mediterranean", "Asian Fusion", "Classic"],
            "includes": ["setup", "service", "cleanup"],
        },
        {
            "name": "Quick Bites Pro",
            "min_guests": 5,
            "max_guests": 25,
            "price_per_person": 30,
            "menu_options": ["Sandwiches", "Salads", "Hot Buffet"],
            "includes": ["delivery", "disposable setup"],
        },
    ]

    def execute(
        self,
        guests: int = 15,
        venue: str = "",
        date: str = "",
        **kwargs,
    ) -> ToolResult:
        """Get available catering options for the event."""
        options = []
        for c in self.CATERERS:
            if c["min_guests"] <= guests <= c["max_guests"]:
                total = guests * c["price_per_person"]
                options.append(
                    f"- {c['name']}: ${c['price_per_person']}/person, "
                    f"total ~${total}, menus: {', '.join(c['menu_options'])}"
                )

        observation = (
            "Catering options:\n" + "\n".join(options)
            if options
            else "No caterers available for this group size."
        )

        return ToolResult(
            tool_name=self.name,
            success=bool(options),
            data={"options": options, "guests": guests},
            observation=observation,
        )
