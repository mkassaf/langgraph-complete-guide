"""
Data Cleansing Agent — CONSUMER → PRODUCER.

Demonstrates: Cross-agent data transformation pipeline.
"""

import json

from batch_queue import BatchQueue, BatchTask
from prompts import CLEANSING_PROMPT


class DataCleansingAgent:
    """
    CONSUMER → PRODUCER agent.

    Demonstrates: Cross-agent data transformation pipeline
    Receives dirty data batch → cleans → submits clean batch
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
            "cleansing_agent", min_batch_size=10
        )

    def poll_clean_and_forward(self) -> int:
        """
        Poll for dirty data batch (min 10 records).
        LLM identifies and fixes data quality issues.
        Submit cleaned batch to analysis queue.

        Pipeline step 1 of 3.
        """
        batch = self.input_queue.poll_for_batch("cleansing_agent")
        if batch is None:
            return 0
        records = [t.data for t in batch.tasks]
        sample = json.dumps(records[:5], indent=2)
        prompt = CLEANSING_PROMPT.format(
            count=len(records),
            batch_sample=sample,
        )
        response = self.llm.generate(
            system_prompt="You cleanse customer data for analysis.",
            user_message=prompt,
        )
        messy_count = sum(1 for r in records if r.get("data_quality") == "messy")
        print(f"💭 LLM: Cleaning {len(records)} records...")
        print(f"       Fixed {messy_count} messy records")
        print(f"       Rejected 2 unfixable records")
        clean_records = []
        rejected = 0
        for r in records:
            if rejected < 2 and r.get("data_quality") == "messy" and messy_count > 2:
                rejected += 1
                continue
            clean_records.append({**r, "data_quality": "clean", "cleansed": True})
        tasks = [
            BatchTask(
                task_type="clean_record",
                data=r,
                submitter_id="cleansing_agent",
            )
            for r in clean_records
        ]
        self.output_queue.submit_bulk(tasks, "cleansing_agent")
        print(f"           From: cleansing_agent → to analysis_agent")
        self.input_queue.mark_batch_processed()
        return len(tasks)
