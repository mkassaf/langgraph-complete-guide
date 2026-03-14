"""
Intra-agent batch queue — learning microservice.

Demonstrates: Learning tasks batched, not real-time.
"""

import json

from batch_queue import BatchQueue, BatchTask
from prompts import LEARNING_BATCH_PROMPT


class IntraAgentLearningPipeline:
    """
    Demonstrates intra-agent batch queue usage.

    From lesson: 'After each microservice performs its
    processing, it can send a task intended for the
    learning microservice so that it learns from the
    details of each processing step. However, these
    learning tasks do not need to be carried out in
    real time.'

    Three microservices send learning tasks:
    - perception_microservice
    - reasoning_microservice
    - action_microservice

    Learning microservice processes batch when ready.
    """

    def __init__(self, llm_client):
        self.llm = llm_client
        self.internal_batch_queue = BatchQueue("internal_learning")
        self.internal_batch_queue.consumer_sets_threshold(
            "learning_microservice", min_batch_size=3
        )

    def _submit_learning_task(self, step_name: str, data: dict):
        """Submit a learning task to internal batch queue."""
        task = BatchTask(
            task_type="learning_step",
            data={"step": step_name, **data},
            submitter_id=step_name,
        )
        self.internal_batch_queue.submit_task(task, quiet=True)
        pending = self.internal_batch_queue.get_pending_count()
        print(f"[INTERNAL BATCH:learning] Task submitted ({pending}/3 pending)")
        if pending >= 3:
            print("→ Threshold reached! Dispatching to learning microservice")

    def simulate_processing_cycle(self, customer_data: dict):
        """
        Simulate one agent processing cycle:
        1. perception_microservice detects customer pattern
        2. reasoning_microservice decides action
        3. action_microservice executes
        4. Each sends learning task to internal batch queue
        5. learning_microservice processes batch when complete
        """
        print("\n🧠 perception_microservice: detecting customer pattern...")
        percept = self._perception_step(customer_data)
        print("🧠 reasoning_microservice: deciding action...")
        decision = self._reasoning_step(percept)
        print("🧠 action_microservice: executing...")
        result = self._action_step(decision)
        self._learning_step()
        return result

    def _perception_step(self, data: dict) -> dict:
        """Simulate perception + submit learning task."""
        is_vip = data.get("amount", 0) > 100 or data.get("customer_id", "").endswith("007")
        percept = {
            "customer_id": data.get("customer_id"),
            "pattern": "VIP customer" if is_vip else "standard",
            "amount": data.get("amount"),
        }
        self._submit_learning_task("perception_microservice", percept)
        return percept

    def _reasoning_step(self, percept: dict) -> dict:
        """Simulate reasoning + submit learning task."""
        decision = {
            "action": "priority_response" if percept.get("pattern") == "VIP customer" else "standard",
            "offer_type": "personalized" if percept.get("pattern") == "VIP customer" else "generic",
        }
        self._submit_learning_task("reasoning_microservice", decision)
        return decision

    def _action_step(self, decision: dict) -> dict:
        """Simulate action + submit learning task."""
        result = {
            "executed": "personalized offer" if decision.get("offer_type") == "personalized" else "generic",
            "success": True,
        }
        self._submit_learning_task("action_microservice", result)
        return result

    def _learning_step(self):
        """
        Learning microservice polls batch queue.
        LLM learns from all 3 steps together.
        Only runs when full batch (3 tasks) is available.
        """
        batch = self.internal_batch_queue.poll_for_batch("learning_microservice")
        if batch is None:
            return
        steps = [t.data for t in batch.tasks]
        prompt = LEARNING_BATCH_PROMPT.format(
            steps=json.dumps(steps, indent=2),
        )
        response = self.llm.generate(
            system_prompt="You extract learnings from processing steps.",
            user_message=prompt,
        )
        print("💭 LLM: Learning from full processing cycle...")
        for line in response.strip().split("\n")[:5]:
            print(f"       {line}")
        self.internal_batch_queue.mark_batch_processed()
