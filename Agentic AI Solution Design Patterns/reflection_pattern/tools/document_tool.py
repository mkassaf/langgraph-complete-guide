"""
Document tool — creates proposal.md.
Fails when date is missing (for Demo 2 error injection).
"""

from pathlib import Path

from tools.base_tool import BaseTool, ToolResult


class DocumentTool(BaseTool):
    name = "document_tool"

    def execute(
        self,
        venue: str = "",
        date: str = "",
        catering: str = "",
        attendees: int = 15,
        activities: list | None = None,
        **kwargs,
    ) -> ToolResult:
        """Create proposal.md. Returns error if date missing (for Demo 2)."""
        activities = activities or ["Team building", "Strategy session"]
        if isinstance(activities, str):
            activities = [activities]

        # Fail when date is missing (controller injects this for Demo 2)
        if not date or str(date).strip() == "" or str(date).lower() == "none":
            return ToolResult(
                tool_name=self.name,
                success=False,
                data={},
                observation="ERROR: date parameter was None or empty. document_tool requires venue, date, catering, attendees.",
            )

        script_dir = Path(__file__).resolve().parent.parent
        output_path = script_dir / "proposal.md"
        content = f"""# Team Offsite Meeting Proposal

## Summary
- **Date:** {date}
- **Venue:** {venue}
- **Catering:** {catering}
- **Attendees:** {attendees}

## Activities
{chr(10).join(f'- {a}' for a in activities)}
"""

        try:
            output_path.write_text(content, encoding="utf-8")
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={"path": str(output_path)},
                observation=f"Proposal saved to {output_path}",
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, data={}, observation=str(e))
