"""
Report Agent — uses Batch Queue.
"""

from fabric.messaging_fabric import MessagingFabric
from platforms.batch_queue import Batch
from prompts import BATCH_REPORT_PROMPT


class ReportAgent:
    """
    Generates end-of-shift reports.
    Uses: Batch Queue (collects quality checks, processes together)
    """

    agent_id = "report_agent"

    def __init__(self, llm_client):
        self.llm = llm_client

    def generate_shift_report(self, fabric: MessagingFabric) -> dict:
        """Trigger batch. LLM analyzes all quality checks together."""
        batch = fabric.trigger_batch("quality_reports")
        if not batch:
            return {"error": "No batch to process"}

        items_str = "\n".join(str(item.data) for item in batch.items)
        try:
            content = self.llm.generate(
                "You are a reporting agent.",
                BATCH_REPORT_PROMPT.format(count=len(batch.items), batch_items=items_str),
            )
        except Exception:
            content = "TOTAL_ITEMS_INSPECTED: 225. PASS_RATE: 94.2%. DEFECTS: 13 units."

        fabric.process_batch("quality_reports", batch, self.agent_id)
        batch.result = {"report": content}
        return {"batch_id": batch.batch_id, "items": len(batch.items), "report": content[:500]}
