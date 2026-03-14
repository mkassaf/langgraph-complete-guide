"""
Development Sub-Orchestrator — Layer 2 Goal-Based Agent.
"""

import re
from layers.layer2_sub_orchestrators.base_sub_orchestrator import BaseSubOrchestrator
from communication.message_router import MessageDirection
from prompts import SUB_ORCHESTRATOR_PLAN_PROMPT


class DevelopmentSubOrchestrator(BaseSubOrchestrator):
    """
    LAYER 2: Goal-Based Agent (Development domain)
    """

    agent_id = "development_orchestrator"
    domain = "development"

    def __init__(self, llm_client, router, tracker):
        super().__init__(llm_client, router, tracker)

    def plan_tasks(self, domain_goals: dict) -> list[dict]:
        """Break development goals into coding, testing, security tasks."""
        tracker = self.tracker
        tracker.update_agent_status(self.agent_id, 2, "in_progress", 0.2)
        try:
            content = self.llm.generate(
                "You are a development sub-orchestrator.",
                SUB_ORCHESTRATOR_PLAN_PROMPT.format(
                    domain="Development",
                    domain_goals=str(domain_goals),
                    available_workers="coding_worker, testing_worker, security_team",
                ),
            )
            return self._parse_tasks(content)
        except Exception:
            return self._fallback_tasks()

    def _parse_tasks(self, content: str) -> list[dict]:
        tasks = []
        for worker in ["coding_worker", "testing_worker", "security_team"]:
            m = re.search(rf"ASSIGN_TO:\s*{worker}.*?TITLE:\s*(.+?)(?=ASSIGN_TO|$)", content, re.S | re.I)
            if m or worker in content.lower():
                tasks.append({
                    "task_id": f"dev_{worker}",
                    "title": f"Development task for {worker}",
                    "assign_to": worker,
                    "description": f"Complete {worker} deliverables",
                    "deliverable": f"{worker} output",
                    "priority": "high",
                })
        return tasks if tasks else self._fallback_tasks()

    def _fallback_tasks(self) -> list[dict]:
        return [
            {"task_id": "dev_1", "title": "Complete 12 remaining features", "assign_to": "coding_worker", "description": "Feature development", "deliverable": "Code complete", "priority": "high"},
            {"task_id": "dev_2", "title": "Achieve 90% test coverage", "assign_to": "testing_worker", "description": "Testing", "deliverable": "Test report", "priority": "high"},
            {"task_id": "dev_3", "title": "Full security audit", "assign_to": "security_team", "description": "Security review", "deliverable": "Audit report", "priority": "high"},
        ]

    def delegate_to_workers(self, tasks: list[dict]):
        """Send tasks to Layer 3 workers."""
        for task in tasks:
            worker_id = task.get("assign_to")
            if worker_id in self.workers:
                self.router.send(
                    self.agent_id, 2, worker_id, 3,
                    MessageDirection.DOWN,
                    {"task": task, "task_context": "development"},
                    "development",
                )

    def collect_and_report(self) -> dict:
        """Aggregate worker results."""
        return self.task_results
