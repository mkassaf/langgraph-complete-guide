"""
State Sync Agent — Coordinated state synchronization.
"""

import json

from batch_queue import BatchQueue
from prompts import SYNC_PROMPT


class StateSyncAgent:
    """
    Demonstrates: Coordinated state synchronization

    From lesson: 'Batch queues can facilitate this by
    efficiently processing periodic updates of the state
    data in the shared agent memory system.'

    Collects scattered state updates and synchronizes
    them periodically in bulk — not in real time.
    """

    def __init__(self, llm_client, sync_queue: BatchQueue):
        self.llm = llm_client
        self.queue = sync_queue
        self.shared_memory: dict = {}
        self.queue.consumer_sets_threshold(
            "sync_agent", min_batch_size=5
        )

    def periodic_sync(self) -> int:
        """
        Collect accumulated state updates.
        Apply them to shared memory in bulk.

        Much more efficient than real-time sync.
        """
        batch = self.queue.poll_for_batch("sync_agent")
        if batch is None:
            return 0
        updates = [t.data for t in batch.tasks]
        prompt = SYNC_PROMPT.format(
            count=len(updates),
            updates=json.dumps(updates[:5], indent=2),
        )
        response = self.llm.generate(
            system_prompt="You synchronize state updates to shared memory.",
            user_message=prompt,
        )
        print(f"💭 LLM: Syncing {len(updates)} state updates to shared memory")
        print(f"       Much more efficient than {len(updates)} individual syncs!")
        for u in updates:
            key = u.get("key", u.get("agent_id", str(hash(str(u)))))
            self.shared_memory[key] = u
        self.queue.mark_batch_processed()
        return len(updates)
