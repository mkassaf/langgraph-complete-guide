"""
Report Agent — CONSUMER.

Demonstrates: End of transformation pipeline.
"""

import json
from datetime import datetime

from batch_queue import BatchQueue
from prompts import REPORT_PROMPT


class ReportAgent:
    """
    CONSUMER agent — final pipeline stage.

    Demonstrates: End of transformation pipeline.
    Generates final business reports from analyzed data.
    """

    def __init__(self, llm_client, input_queue: BatchQueue):
        self.llm = llm_client
        self.queue = input_queue
        self.queue.consumer_sets_threshold(
            "report_agent", min_batch_size=5
        )

    def poll_and_generate_report(self) -> str | None:
        """
        Poll for analysis results batch.
        LLM synthesizes into business report.

        Pipeline step 3 of 3.
        """
        batch = self.queue.poll_for_batch("report_agent")
        if batch is None:
            return None
        analyses = [t.data for t in batch.tasks]
        prompt = REPORT_PROMPT.format(
            count=len(analyses),
            analyses=json.dumps(analyses[:3], indent=2),
            date=datetime.now().strftime("%Y-%m-%d"),
        )
        response = self.llm.generate(
            system_prompt="You generate executive business reports.",
            user_message=prompt,
        )
        print(f"💭 LLM: Generating executive report...")
        print(f"       [Full report output]")
        self.queue.mark_batch_processed()
        return response
