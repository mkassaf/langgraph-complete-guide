"""
Data Collector Agent — PRODUCER.

Demonstrates: Asynchronous bulk message exchange.
"""

import json

from batch_queue import BatchQueue, BatchTask
from prompts import DATA_VALIDATION_PROMPT


class DataCollectorAgent:
    """
    PRODUCER agent — collects customer data records.

    Demonstrates: Asynchronous bulk message exchange
    Submits large batches without waiting for processing.
    """

    RAW_DATA = [
        {
            "record_id": f"REC-{i:03d}",
            "customer_id": f"CUST-{(i % 50) + 1:03d}",
            "event": "purchase",
            "amount": round(10 + i * 2.5, 2),
            "timestamp": f"2024-01-{(i % 28) + 1:02d}",
            "raw_category": ["electronics", "clothing", "food"][i % 3],
            "data_quality": ["clean", "clean", "messy", "clean"][i % 4],
        }
        for i in range(1, 51)
    ]

    def __init__(self, llm_client, batch_queue: BatchQueue):
        self.llm = llm_client
        self.queue = batch_queue

    def collect_and_submit(self):
        """
        LLM validates data quality.
        Submit all 50 records as BULK to batch queue.
        Continue immediately — don't wait!

        Demonstrates: bulk message exchange
        """
        sample = json.dumps(self.RAW_DATA[:5], indent=2)
        prompt = DATA_VALIDATION_PROMPT.format(
            total=len(self.RAW_DATA),
            sample_records=sample,
        )
        response = self.llm.generate(
            system_prompt="You validate customer data batches.",
            user_message=prompt,
        )
        messy = sum(1 for r in self.RAW_DATA if r.get("data_quality") == "messy")
        clean = len(self.RAW_DATA) - messy
        print(f"💭 LLM: Validating 50 records... {clean} clean, {messy} messy")
        tasks = [
            BatchTask(
                task_type="customer_record",
                data=r,
                submitter_id="data_collector_agent",
            )
            for r in self.RAW_DATA
        ]
        self.queue.submit_bulk(tasks, "data_collector_agent")
