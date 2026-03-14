"""
Regulatory Reporting Agent — CONSUMER

Listens for risk profile reports. Operates on scheduled basis (daily/weekly).
Consolidates high-risk data, generates compliance/SAR reports, formats
per regulatory standards, submits to authorities.
"""

import json
from datetime import datetime

from batch_queue import BatchQueue
from prompts import REGULATORY_REPORT_PROMPT


class RegulatoryReportingAgent:
    """
    Final consumer. Receives risk profile reports. Consolidates data,
    generates compliance reports, formats for regulatory submission.
    """

    def __init__(self, llm_client, input_queue: BatchQueue):
        self.llm = llm_client
        self.queue = input_queue
        self.queue.consumer_sets_threshold(
            "regulatory_reporting_agent", min_batch_size=1
        )

    def poll_and_report(self) -> str | None:
        """
        Poll for risk profile reports. Consolidate, generate
        compliance/SAR reports, format for authorities.
        """
        batch = self.queue.poll_for_batch("regulatory_reporting_agent")
        if batch is None:
            return None
        reports = [t.data for t in batch.tasks]
        prompt = REGULATORY_REPORT_PROMPT.format(
            risk_reports=json.dumps(reports, indent=2),
        )
        response = self.llm.generate(
            system_prompt="You generate regulatory compliance reports.",
            user_message=prompt,
        )
        print(f"📋 regulatory_reporting_agent: Processing {len(reports)} risk report(s)")
        print("   Consolidating high-risk data...")
        print("   Generating SAR & compliance reports...")
        print("   → Formatted per regulatory standards, ready for submission")
        self.queue.mark_batch_processed()
        return response
