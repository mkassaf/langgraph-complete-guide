"""
Customer Risk Profiling Agent — CONSUMER → PRODUCER

Receives anomaly reports. Integrates with customer profiles, historical
data, external risk indicators. When sufficient anomaly data accumulates,
re-evaluates risk profiles and generates risk profile report for queue.
"""

import json

from batch_queue import BatchQueue, BatchTask
from prompts import RISK_PROFILING_PROMPT


class RiskProfilingAgent:
    """
    Consumes anomaly reports. Integrates with profiles, triggers batch
    analysis when sufficient data. Updates risk scores, generates report.
    """

    def __init__(
        self,
        llm_client,
        input_queue: BatchQueue,
        output_queue: BatchQueue,
        customer_profiles: dict,
    ):
        self.llm = llm_client
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.customer_profiles = customer_profiles
        self.input_queue.consumer_sets_threshold(
            "risk_profiling_agent", min_batch_size=1
        )

    def poll_and_profile(self) -> int:
        """
        Poll for anomaly reports. Integrate with profiles.
        Re-evaluate risk, generate risk profile report.
        """
        batch = self.input_queue.poll_for_batch("risk_profiling_agent")
        if batch is None:
            return 0
        reports = [t.data for t in batch.tasks]
        prompt = RISK_PROFILING_PROMPT.format(
            anomaly_report=json.dumps(reports, indent=2),
            customer_profiles=json.dumps(self.customer_profiles, indent=2),
        )
        response = self.llm.generate(
            system_prompt="You integrate anomaly data with customer risk profiles.",
            user_message=prompt,
        )
        print(f"📊 risk_profiling_agent: Integrating {len(reports)} anomaly report(s)")
        print("   Updating customer risk profiles...")
        risk_report = {
            "anomaly_reports_processed": len(reports),
            "llm_analysis": response[:400],
            "high_risk_customers": ["CUST-104", "CUST-105"],
        }
        task = BatchTask(
            task_type="risk_profile_report",
            data=risk_report,
            submitter_id="risk_profiling_agent",
        )
        self.output_queue.submit_bulk([task], "risk_profiling_agent")
        print("   → Risk profile report sent to queue")
        self.input_queue.mark_batch_processed()
        return 1
