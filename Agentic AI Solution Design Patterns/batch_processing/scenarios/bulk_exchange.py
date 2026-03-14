"""
Use Case 1: Asynchronous bulk message exchange.
"""

from batch_queue import BatchQueue, BatchTask
from agents import DataCollectorAgent


def run_bulk_exchange(llm_client) -> BatchQueue:
    """Data collector submits 50 records in single bulk operation."""
    queue = BatchQueue("raw_data")
    collector = DataCollectorAgent(llm_client, queue)
    collector.collect_and_submit()
    return queue
