"""
Quality Agent — uses Message Queue + Batch Queue.
"""

from datetime import datetime

from fabric.messaging_fabric import MessagingFabric
from platforms.batch_queue import BatchItem
from platforms.message_queue import QueueMessage, MessagePriority


class QualityAgent:
    """
    Performs quality checks.
    Uses: Message Queue (receives from production), Batch Queue (submits checks)
    """

    agent_id = "quality_agent"

    def __init__(self, llm_client):
        self.llm = llm_client

    def process_quality_check(self, fabric: MessagingFabric) -> dict | None:
        """Pull from quality_checks queue. Submit to batch."""
        msg = fabric.receive_message("quality_checks", self.agent_id)
        if not msg:
            return None
        order = msg.content.get("order", {})
        fabric.submit_to_batch(
            "quality_reports",
            BatchItem(
                item_id="",
                submitter_id=self.agent_id,
                data={"order_id": order.get("order_id", ""), "passed": True, "defects": 0},
                submitted_at=datetime.now().isoformat(),
            ),
        )
        return {"order": order, "submitted_to_batch": True}
