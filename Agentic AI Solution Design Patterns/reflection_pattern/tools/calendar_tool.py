"""Calendar tool — team availability."""

from tools.base_tool import BaseTool, ToolResult


class CalendarTool(BaseTool):
    name = "calendar_tool"
    AVAILABILITY = {
        "Alice": ["15th", "18th", "22nd"],
        "Bob": ["14th", "18th", "22nd"],
        "Carol": ["15th", "18th", "20th"],
        "Dave": ["18th", "22nd", "25th"],
        "Eve": ["15th", "18th", "23rd"],
    }

    def execute(self, team=None, month="next_month", duration="half_day", **kwargs) -> ToolResult:
        team = team or list(self.AVAILABILITY.keys())
        if isinstance(team, str):
            team = [t.strip() for t in team.replace(",", " ").split() if t.strip()]
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
            else "No common dates found."
        )
        return ToolResult(tool_name=self.name, success=bool(common_dates), data={"common_dates": common_dates}, observation=observation)
