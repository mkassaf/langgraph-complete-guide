"""
Transaction Ingest Agent — PRODUCER

Receives transaction data from various sources (online banking, credit card,
ATMs, wire transfers). Sends raw data to batch queue without waiting.
Continues collecting the next set of transactions.
"""

import json

from batch_queue import BatchQueue, BatchTask
from prompts import INGEST_VALIDATION_PROMPT


class TransactionIngestAgent:
    """
    Initial producer that receives transaction data from various sources.
    Sends messages to batch queue, doesn't wait for further processing.
    """

    def __init__(self, llm_client, batch_queue: BatchQueue):
        self.llm = llm_client
        self.queue = batch_queue

    def ingest_and_submit(self, transactions: list[dict]):
        """
        Validate transactions and submit to batch queue.
        Does NOT wait for processing — continues immediately.
        """
        sources = list({t.get("source", "?") for t in transactions})
        sample = json.dumps(transactions[:4], indent=2)
        prompt = INGEST_VALIDATION_PROMPT.format(
            sources=sources,
            count=len(transactions),
            sample=sample,
        )
        self.llm.generate(
            system_prompt="You validate transaction data for batch processing.",
            user_message=prompt,
        )
        print(f"📥 transaction_ingest_agent: Received {len(transactions)} from {sources}")
        print("   Sending to batch queue — not waiting for analysis ✓")
        tasks = [
            BatchTask(
                task_type="raw_transaction",
                data=t,
                submitter_id="transaction_ingest_agent",
            )
            for t in transactions
        ]
        self.queue.submit_bulk(tasks, "transaction_ingest_agent")
