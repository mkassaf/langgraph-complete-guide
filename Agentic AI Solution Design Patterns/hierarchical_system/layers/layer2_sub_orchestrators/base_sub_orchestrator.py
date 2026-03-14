"""
Base sub-orchestrator — abstract Layer 2 agent.
"""

from abc import ABC, abstractmethod


class BaseSubOrchestrator(ABC):
    """
    LAYER 2: Goal-Based Agent (base)
    Sub-orchestrators receive domain goals and delegate to workers.
    """

    agent_id: str = ""
    domain: str = ""

    def __init__(self, llm_client, router, tracker):
        self.llm = llm_client
        self.router = router
        self.tracker = tracker
        self.workers: dict[str, object] = {}
        self.task_results: dict[str, dict] = {}

    @abstractmethod
    def plan_tasks(self, domain_goals: dict) -> list[dict]:
        """Break domain goals into worker tasks."""
        ...

    @abstractmethod
    def delegate_to_workers(self, tasks: list[dict]):
        """Send tasks to Layer 3 workers."""
        ...

    @abstractmethod
    def collect_and_report(self) -> dict:
        """Aggregate worker results, report to Layer 1."""
        ...
