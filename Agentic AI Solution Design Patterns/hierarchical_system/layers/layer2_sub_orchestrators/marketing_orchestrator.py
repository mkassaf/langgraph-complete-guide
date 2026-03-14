"""
Marketing Sub-Orchestrator — Layer 2 Goal-Based Agent.
"""

import re
from layers.layer2_sub_orchestrators.base_sub_orchestrator import BaseSubOrchestrator
from communication.message_router import MessageDirection
from prompts import SUB_ORCHESTRATOR_PLAN_PROMPT


class MarketingSubOrchestrator(BaseSubOrchestrator):
    """
    LAYER 2: Goal-Based Agent (Marketing domain)
    """

    agent_id = "marketing_orchestrator"
    domain = "marketing"

    def __init__(self, llm_client, router, tracker):
        super().__init__(llm_client, router, tracker)

    def plan_tasks(self, domain_goals: dict) -> list[dict]:
        """Break marketing goals into content and campaign tasks."""
        self.tracker.update_agent_status(self.agent_id, 2, "in_progress", 0.2)
        try:
            content = self.llm.generate(
                "You are a marketing sub-orchestrator.",
                SUB_ORCHESTRATOR_PLAN_PROMPT.format(
                    domain="Marketing",
                    domain_goals=str(domain_goals),
                    available_workers="content_worker, campaign_worker",
                ),
            )
            return self._parse_tasks(content)
        except Exception:
            return self._fallback_tasks()

    def _parse_tasks(self, content: str) -> list[dict]:
        tasks = []
        for worker in ["content_worker", "campaign_worker"]:
            if worker in content.lower():
                tasks.append({
                    "task_id": f"mkt_{worker}",
                    "title": f"Marketing task for {worker}",
                    "assign_to": worker,
                    "description": f"Complete {worker} deliverables",
                    "deliverable": f"{worker} output",
                    "priority": "high",
                })
        return tasks if tasks else self._fallback_tasks()

    def _fallback_tasks(self) -> list[dict]:
        return [
            {"task_id": "mkt_1", "title": "Create content in 15 languages", "assign_to": "content_worker", "description": "Multilingual content", "deliverable": "Content assets", "priority": "high"},
            {"task_id": "mkt_2", "title": "Set up digital campaigns", "assign_to": "campaign_worker", "description": "Campaign setup", "deliverable": "Campaigns configured", "priority": "high"},
        ]

    def delegate_to_workers(self, tasks: list[dict]):
        """Send tasks to Layer 3 workers."""
        for task in tasks:
            worker_id = task.get("assign_to")
            if worker_id in self.workers:
                self.router.send(
                    self.agent_id, 2, worker_id, 3,
                    MessageDirection.DOWN,
                    {"task": task, "task_context": "marketing"},
                    "marketing",
                )

    def collect_and_report(self) -> dict:
        """Aggregate worker results."""
        return self.task_results
