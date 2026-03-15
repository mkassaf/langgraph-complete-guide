"""
Procedural memory — skill templates from successful actions.

From lesson: 'formats them into a reusable skill template for use
with the in-context learning pattern'
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SkillTemplate:
    """A reusable skill template from successful actions."""

    template_id: str
    task_type: str
    optimal_tool_sequence: list[str]
    tool_latencies: dict[str, float]
    success_rate: float
    notes: str
    timestamp: str


class ProceduralStore:
    def create_skill_template(self, action_metrics: dict) -> SkillTemplate:
        """Package action metrics into skill template."""
        seq = action_metrics.get("successful_sequence", action_metrics.get("tools_used", []))
        latencies = action_metrics.get("tool_latencies", {})
        return SkillTemplate(
            template_id=action_metrics.get("template_id", f"PR-{datetime.now().strftime('%H%M%S')}"),
            task_type=action_metrics.get("task_type", "meeting"),
            optimal_tool_sequence=seq,
            tool_latencies=latencies,
            success_rate=1.0 if action_metrics.get("outcome") == "success" else 0.0,
            notes=action_metrics.get("note", ""),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

    def get_optimal_sequence(
        self, task_type: str, group_size: int
    ) -> list[str] | None:
        """Return most efficient tool sequence for task type."""
        return None
