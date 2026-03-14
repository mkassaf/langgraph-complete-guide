"""
Use Case 3: Workload delegation.

Data collector delegates analysis to specialized analysis agent.
"""

from batch_queue import BatchQueue
from agents import DataCollectorAgent, DataCleansingAgent, AnalysisAgent


def run_workload_delegation(llm_client) -> dict:
    """Data collector produces data; cleansing delegates to analysis specialist."""
    raw_queue = BatchQueue("raw_data")
    clean_queue = BatchQueue("clean_data")
    analysis_queue = BatchQueue("analysis")
    collector = DataCollectorAgent(llm_client, raw_queue)
    cleansing = DataCleansingAgent(llm_client, raw_queue, clean_queue)
    analysis = AnalysisAgent(llm_client, clean_queue, analysis_queue)
    collector.collect_and_submit()
    cleansing.poll_clean_and_forward()
    analysis.poll_analyze_and_forward()
    return {"raw": raw_queue, "clean": clean_queue, "analysis": analysis_queue}
