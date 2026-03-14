"""
ReAct Tools — Calendar Tool

Simulates checking team calendar availability.
In production this would call Google Calendar API etc.
"""

from tools.base_tool import BaseTool, ToolResult


class CalendarTool(BaseTool):
    """
    Simulates checking team calendar availability.
    In production this would call Google Calendar API etc.
    """

    name = "calendar_tool"

    AVAILABILITY = {
        "Alice": ["15th", "18th", "22nd"],
        "Bob": ["14th", "18th", "22nd"],
        "Carol": ["15th", "18th", "20th"],
        "Dave": ["18th", "22nd", "25th"],
        "Eve": ["15th", "18th", "23rd"],
    }

    def execute(
        self,
        team: list | None = None,
        month: str = "next_month",
        duration: str = "half_day",
        **kwargs,
    ) -> ToolResult:
        """
        Find dates when ALL team members are available.
        Returns ToolResult with common available dates.
        """
        team = team or list(self.AVAILABILITY.keys())
        if isinstance(team, str):
            team = [t.strip() for t in team.replace(",", " ").split() if t.strip()]
        # Normalize names (handle partial matches)
        available_sets = []
        for member in team:
            for key in self.AVAILABILITY:
                if member.lower() in key.lower() or key.lower() in str(member).lower():
                    available_sets.append(set(self.AVAILABILITY[key]))
                    break
            else:
                available_sets.append(set(self.AVAILABILITY.get(member, [])))

        if not available_sets:
            available_sets = [set(dates) for dates in self.AVAILABILITY.values()]

        common = set.intersection(*available_sets) if available_sets else set()
        common_dates = sorted(common, key=lambda x: int("".join(c for c in x if c.isdigit()) or 0))

        observation = (
            f"Common available dates: {', '.join(common_dates)}\n"
            f"All {len(team)} team members free on these dates."
            if common_dates
            else "No common dates found. Team availability conflicts."
        )

        return ToolResult(
            tool_name=self.name,
            success=bool(common_dates),
            data={"common_dates": common_dates, "team": team},
            observation=observation,
        )
