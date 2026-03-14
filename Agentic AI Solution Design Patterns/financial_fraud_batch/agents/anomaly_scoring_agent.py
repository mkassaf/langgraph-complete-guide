"""
Anomaly Scoring Agent — CONSUMER → PRODUCER

Periodically polls batch queue. When sufficient transactions accumulate,
processes the batch together: statistical anomalies, unusual patterns,
deviations from typical behavior. Assigns fraud risk scores and sends
anomaly batch report back to the queue.
"""

import json

from batch_queue import BatchQueue, BatchTask
from prompts import ANOMALY_SCORING_PROMPT


class AnomalyScoringAgent:
    """
    Polls for transaction batches. Processes together to detect
    anomalies and assign fraud risk scores. Sends anomaly report to queue.
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
            "anomaly_scoring_agent", min_batch_size=5
        )

    def poll_and_score(self) -> int:
        """
        Poll for transaction batch. Process together, assign scores,
        send anomaly batch report to queue.
        """
        batch = self.input_queue.poll_for_batch("anomaly_scoring_agent")
        if batch is None:
            return 0
        transactions = [t.data for t in batch.tasks]
        prompt = ANOMALY_SCORING_PROMPT.format(
            count=len(transactions),
            batch=json.dumps(transactions, indent=2),
        )
        response = self.llm.generate(
            system_prompt="You detect fraud anomalies in transaction batches.",
            user_message=prompt,
        )
        print(f"🔍 anomaly_scoring_agent: Processing batch of {len(transactions)}")
        print("   Analyzing anomalies, assigning fraud risk scores...")
        scores = [70 if t.get("amount", 0) > 10000 else (50 if t.get("amount", 0) > 1000 else 20) for t in transactions]
        anomaly_report = {
            "transaction_count": len(transactions),
            "fraud_scores": dict(zip([t.get("txn_id") for t in transactions], scores)),
            "llm_analysis": response[:400],
            "high_risk_count": sum(1 for s in scores if s >= 70),
        }
        task = BatchTask(
            task_type="anomaly_batch_report",
            data=anomaly_report,
            submitter_id="anomaly_scoring_agent",
        )
        self.output_queue.submit_bulk([task], "anomaly_scoring_agent")
        print(f"   → Anomaly report sent to queue ({anomaly_report['high_risk_count']} high-risk)")
        self.input_queue.mark_batch_processed()
        return 1
