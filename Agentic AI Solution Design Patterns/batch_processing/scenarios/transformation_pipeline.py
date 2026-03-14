"""
Use Case 4: Cross-agent data transformation pipeline.

Stage 1: Cleansing → Stage 2: Analysis → Stage 3: Reporting
"""

from batch_queue import BatchQueue
from agents import (
    DataCollectorAgent,
    DataCleansingAgent,
    AnalysisAgent,
    ReportAgent,
)


def run_transformation_pipeline(llm_client) -> dict:
    """Full pipeline: raw → clean → analyze → report."""
    raw_queue = BatchQueue("raw_data")
    clean_queue = BatchQueue("clean_data")
    analysis_queue = BatchQueue("analysis")
    report_queue = BatchQueue("report")
    collector = DataCollectorAgent(llm_client, raw_queue)
    cleansing = DataCleansingAgent(llm_client, raw_queue, clean_queue)
    analysis = AnalysisAgent(llm_client, clean_queue, analysis_queue)
    report = ReportAgent(llm_client, analysis_queue)
    collector.collect_and_submit()
    print("\nSTAGE 1 - CLEANSING:")
    cleansing.poll_clean_and_forward()
    print("\nSTAGE 2 - ANALYSIS:")
    analysis.poll_analyze_and_forward()
    print("\nSTAGE 3 - REPORTING:")
    report.poll_and_generate_report()
    return {
        "raw": raw_queue,
        "clean": clean_queue,
        "analysis": analysis_queue,
        "report": report_queue,
    }
