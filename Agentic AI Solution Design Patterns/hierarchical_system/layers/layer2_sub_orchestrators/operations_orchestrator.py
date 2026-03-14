"""
Operations Sub-Orchestrator — Layer 2 Goal-Based Agent.
"""

import re
from layers.layer2_sub_orchestrators.base_sub_orchestrator import BaseSubOrchestrator
from communication.message_router import MessageDirection
from prompts import SUB_ORCHESTRATOR_PLAN_PROMPT


class OperationsSubOrchestrator(BaseSubOrchestrator):
    """
    LAYER 2: Goal-Based Agent (Operations domain)
    """

    agent_id = "operations_orchestrator"
    domain = "operations"

    def __init__(self, llm_client, router, tracker):
        super().__init__(llm_client, router, tracker)

    def plan_tasks(self, domain_goals: dict) -> list[dict]:
        """Break operations goals into deployment and legal tasks."""
        self.tracker.update_agent_status(self.agent_id, 2, "in_progress", 0.2)
        try:
            content = self.llm.generate(
                "You are an operations sub-orchestrator.",
                SUB_ORCHESTRATOR_PLAN_PROMPT.format(
                    domain="Operations",
                    domain_goals=str(domain_goals),
                    available_workers="deployment_worker, logistics_worker, legal_team",
                ),
            )
            return self._parse_tasks(content)
        except Exception:
            return self._fallback_tasks()

    def _parse_tasks(self, content: str) -> list[dict]:
        tasks = []
        for worker in ["deployment_worker", "logistics_worker", "legal_team"]:
            if worker in content.lower():
                tasks.append({
                    "task_id": f"ops_{worker}",
                    "title": f"Operations task for {worker}",
                    "assign_to": worker,
                    "description": f"Complete {worker} deliverables",
                    "deliverable": f"{worker} output",
                    "priority": "high",
                })
        return tasks if tasks else self._fallback_tasks()

    def _fallback_tasks(self) -> list[dict]:
        return [
            {"task_id": "ops_1", "title": "Deploy to AWS 3 regions", "assign_to": "deployment_worker", "description": "Cloud deployment", "deliverable": "Deployed", "priority": "high"},
            {"task_id": "ops_2", "title": "Compliance for EU, US, APAC", "assign_to": "legal_team", "description": "Legal compliance", "deliverable": "Compliance report", "priority": "high"},
        ]

    def delegate_to_workers(self, tasks: list[dict]):
        """Send tasks to Layer 3 workers."""
        for task in tasks:
            worker_id = task.get("assign_to")
            if worker_id in self.workers:
                self.router.send(
                    self.agent_id, 2, worker_id, 3,
                    MessageDirection.DOWN,
                    {"task": task, "task_context": "operations"},
                    "operations",
                )

    def collect_and_report(self) -> dict:
        """Aggregate worker results."""
        return self.task_results
