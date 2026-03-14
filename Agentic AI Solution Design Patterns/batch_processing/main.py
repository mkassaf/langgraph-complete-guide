"""
Batch Processing Architecture — Entry Point

Data analytics platform demonstrating 5 use cases:
1. Asynchronous bulk message exchange
2. Coordinated state synchronization
3. Workload delegation
4. Cross-agent data transformation pipeline
5. Intra-agent batch queue (learning microservice)
"""

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from dotenv import load_dotenv

_env_path = os.path.join(_SCRIPT_DIR, "..", "..", ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
else:
    load_dotenv()

from batch_queue import BatchQueue, BatchTask
from llm_client import LLMClient
from agents import (
    DataCollectorAgent,
    DataCleansingAgent,
    AnalysisAgent,
    ReportAgent,
    StateSyncAgent,
)
from intra_agent.learning_pipeline import IntraAgentLearningPipeline


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║     BATCH PROCESSING ARCHITECTURE DEMONSTRATION     ║
║         Data Analytics Pipeline - 5 Use Cases      ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()

    # ━━━ USE CASE 1: BULK MESSAGE EXCHANGE ━━━
    print("━" * 60)
    print("USE CASE 1: ASYNCHRONOUS BULK MESSAGE EXCHANGE")
    print("━" * 60)
    raw_queue = BatchQueue("raw_data")
    collector = DataCollectorAgent(llm, raw_queue)
    collector.collect_and_submit()

    # ━━━ USE CASE 4: TRANSFORMATION PIPELINE ━━━
    print("\n" + "━" * 60)
    print("USE CASE 4: CROSS-AGENT TRANSFORMATION PIPELINE")
    print("━" * 60)
    clean_queue = BatchQueue("clean_data")
    analysis_queue = BatchQueue("analysis")
    cleansing = DataCleansingAgent(llm, raw_queue, clean_queue)
    analysis = AnalysisAgent(llm, clean_queue, analysis_queue)
    report = ReportAgent(llm, analysis_queue)

    print("\nSTAGE 1 - CLEANSING:")
    cleansing.poll_clean_and_forward()

    print("\nSTAGE 2 - ANALYSIS:")
    analysis.poll_analyze_and_forward()

    print("\nSTAGE 3 - REPORTING:")
    report.poll_and_generate_report()

    # ━━━ USE CASE 2: STATE SYNCHRONIZATION ━━━
    print("\n" + "━" * 60)
    print("USE CASE 2: COORDINATED STATE SYNCHRONIZATION")
    print("━" * 60)
    sync_queue = BatchQueue("state_sync")
    sync_agent = StateSyncAgent(llm, sync_queue)
    state_updates = [
        {"key": "collector_state", "agent_id": "data_collector", "records_processed": 50},
        {"key": "cleansing_state", "agent_id": "cleansing_agent", "records_cleaned": 48},
        {"key": "analysis_state", "agent_id": "analysis_agent", "analyses_done": 48},
        {"key": "report_state", "agent_id": "report_agent", "reports_generated": 1},
        {"key": "cache_state", "agent_id": "cache_agent", "entries": 120},
        {"key": "metrics_state", "agent_id": "metrics_agent", "events": 200},
        {"key": "audit_state", "agent_id": "audit_agent", "checks": 15},
        {"key": "alerts_state", "agent_id": "alerts_agent", "thresholds": 5},
    ]
    tasks = [
        BatchTask(task_type="state_update", data=u, submitter_id=u["agent_id"])
        for u in state_updates
    ]
    sync_queue.submit_bulk(tasks, "various_agents")
    print(f"[BATCH QUEUE:{sync_queue.name}] {len(state_updates)} state updates accumulated\n")
    sync_agent.periodic_sync()

    # ━━━ USE CASE 5: INTRA-AGENT LEARNING ━━━
    print("\n" + "━" * 60)
    print("USE CASE 5: INTRA-AGENT LEARNING PIPELINE")
    print("━" * 60)
    learning = IntraAgentLearningPipeline(llm)
    sample_customer = {
        "customer_id": "CUST-007",
        "amount": 150.0,
        "event": "purchase",
    }
    learning.simulate_processing_cycle(sample_customer)

    # ━━━ FINAL SUMMARY ━━━
    print("\n" + "━" * 60)
    print("BATCH PROCESSING RESULTS")
    print("━" * 60)
    print("""
╔══════════════════════════════════════════════════════╗
║          BATCH PROCESSING RESULTS                   ║
╠══════════════════════════════════════════════════════╣
║ Use Case 1 - Bulk Exchange:                         ║
║   50 records submitted in single bulk operation     ║
║                                                     ║
║ Use Case 2 - State Sync:                            ║
║   8 updates synced in 1 batch (vs 8 individual)    ║
║                                                     ║
║ Use Case 3 - Workload Delegation:                   ║
║   data_collector delegated analysis to specialist   ║
║                                                     ║
║ Use Case 4 - Transformation Pipeline:              ║
║   50 → cleaned → analyzed → reported (3 stages)    ║
║                                                     ║
║ Use Case 5 - Intra-Agent:                           ║
║   3 microservice steps learned as one batch         ║
╠══════════════════════════════════════════════════════╣
║ Consumer threshold control demonstrated:             ║
║   cleansing_agent: waited for 10+ tasks             ║
║   analysis_agent:  waited for 8+ tasks             ║
║   report_agent:    waited for 5+ tasks              ║
║   learning_ms:     waited for 3 tasks (full cycle)  ║
╚══════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
