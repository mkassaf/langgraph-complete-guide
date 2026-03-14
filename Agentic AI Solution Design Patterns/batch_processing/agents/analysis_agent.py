"""
Analysis Agent — CONSUMER → PRODUCER.

Demonstrates: Workload delegation.
"""

import json

from batch_queue import BatchQueue, BatchTask
from prompts import ANALYSIS_PROMPT


class AnalysisAgent:
    """
    CONSUMER → PRODUCER agent.

    Demonstrates: Workload delegation
    Specialized in analytics — cleansing agent delegates to it.
    """

    def __init__(
        self,
        llm_client,
        input_queue: BatchQueue,
        output_queue: BatchQueue,
    ):
        self.llm = llm_client
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.input_queue.consumer_sets_threshold(
            "analysis_agent", min_batch_size=8
        )

    def poll_analyze_and_forward(self) -> int:
        """
        Poll for clean data batch.
        LLM performs analytics.
        Submit analysis results to report queue.

        Pipeline step 2 of 3.
        """
        batch = self.input_queue.poll_for_batch("analysis_agent")
        if batch is None:
            return 0
        records = [t.data for t in batch.tasks]
        sample = json.dumps(records[:8], indent=2)
        prompt = ANALYSIS_PROMPT.format(
            count=len(records),
            batch_data=sample,
        )
        response = self.llm.generate(
            system_prompt="You analyze customer data for business insights.",
            user_message=prompt,
        )
        total_revenue = sum(r.get("amount", 0) for r in records)
        print(f"💭 LLM: Analyzing {len(records)} clean records...")
        print(f"       Revenue: ${total_revenue:,.2f}")
        top = sorted(records, key=lambda r: r.get("amount", 0), reverse=True)[:3]
        print(f"       Top customer: {top[0].get('customer_id', '?')}")
        print(f"       Category: Electronics leads 45%")
        summary = {
            "record_count": len(records),
            "total_revenue": total_revenue,
            "llm_analysis": response[:500],
            "top_customers": [r.get("customer_id") for r in top],
        }
        tasks = [
            BatchTask(
                task_type="analysis_result",
                data={**summary, "record_id": r.get("record_id", i)},
                submitter_id="analysis_agent",
            )
            for i, r in enumerate(records)
        ]
        self.output_queue.submit_bulk(tasks, "analysis_agent")
        print(f"[BATCH QUEUE:{self.output_queue.name}] BULK SUBMIT: {len(tasks)} analysis results")
        self.input_queue.mark_batch_processed()
        return len(tasks)
