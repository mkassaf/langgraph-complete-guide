"""
ReAct Tools — Document Tool

Creates a formal meeting proposal document.
"""

import os
from pathlib import Path

from tools.base_tool import BaseTool, ToolResult


class DocumentTool(BaseTool):
    """
    Creates a formal meeting proposal document.
    Saves as markdown file.
    """

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
        """
        Generate and save proposal.md with full meeting details.
        Returns confirmation with file path.
        """
        activities = activities or ["Team building", "Strategy session", "Networking"]
        if isinstance(activities, str):
            activities = [activities]

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

## Logistics
- In-person event
- Half-day duration
- All team members confirmed available
"""

        try:
            output_path.write_text(content, encoding="utf-8")
            observation = f"Proposal saved to {output_path}\nDocument created successfully."
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={"path": str(output_path), "content": content},
                observation=observation,
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                data={},
                observation=f"Failed to save document: {e}",
            )
