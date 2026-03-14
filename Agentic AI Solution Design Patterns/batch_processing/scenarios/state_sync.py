"""
Use Case 2: Coordinated state synchronization.
"""

from batch_queue import BatchQueue, BatchTask
from agents import StateSyncAgent


def run_state_sync(llm_client) -> tuple[BatchQueue, StateSyncAgent]:
    """Multiple agents submit state updates; sync agent processes in bulk."""
    queue = BatchQueue("state_sync")
    sync_agent = StateSyncAgent(llm_client, queue)
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
    queue.submit_bulk(tasks, "various_agents")
    print(f"[BATCH QUEUE:{queue.name}] {len(state_updates)} state updates accumulated")
    sync_agent.periodic_sync()
    return queue, sync_agent
