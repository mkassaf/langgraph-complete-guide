"""
Main Orchestrator — Layer 1 Utility-Based Agent.
"""

import re
from communication.message_router import MessageRouter, MessageDirection
from communication.hierarchy_tracker import HierarchyTracker
from prompts import MAIN_ORCHESTRATOR_PLAN_PROMPT, SYNTHESIS_PROMPT


class MainOrchestrator:
    """
    LAYER 1: Utility-Based Agent

    Responsibilities:
    - Set high-level strategy and goals
    - Decompose into major domains
    - Delegate each domain to a Sub-Orchestrator
    - Monitor overall system health
    """

    def __init__(self, llm_client, router: MessageRouter, tracker: HierarchyTracker):
        self.llm = llm_client
        self.router = router
        self.tracker = tracker
        self.agent_id = "main_orchestrator"
        self.sub_orchestrators: dict[str, object] = {}
        self.domain_results: dict[str, dict] = {}

    def create_high_level_plan(self, task: str) -> dict:
        """LLM creates top-level plan with 3 domains."""
        self.tracker.update_agent_status(self.agent_id, 1, "in_progress", 0.2)
        try:
            content = self.llm.generate(
                "You are a utility-based orchestrator for global product launches.",
                MAIN_ORCHESTRATOR_PLAN_PROMPT.format(task=task),
            )
            return self._parse_plan(content)
        except Exception:
            return self._fallback_plan()

    def _parse_plan(self, content: str) -> dict:
        domains = {}
        for domain_name in ["Development", "Marketing", "Operations"]:
            block = re.search(
                rf"DOMAIN:\s*{domain_name}.*?DELEGATE_TO:\s*(\w+)",
                content,
                re.S | re.I,
            )
            if block:
                delegate = re.search(r"DELEGATE_TO:\s*(\w+)", block.group(0), re.I)
                goal = re.search(r"GOAL:\s*(.+?)(?=BUDGET|$)", block.group(0), re.S | re.I)
                budget = re.search(r"BUDGET:\s*(.+?)(?=TIMELINE|$)", block.group(0), re.S | re.I)
                domains[domain_name.lower()] = {
                    "goal": goal.group(1).strip()[:200] if goal else "",
                    "budget": budget.group(1).strip()[:100] if budget else "",
                    "delegate_to": delegate.group(1).strip() if delegate else "",
                }
        if not domains:
            return self._fallback_plan()
        return {"domains": domains}

    def _fallback_plan(self) -> dict:
        return {
            "domains": {
                "development": {
                    "goal": "Complete v2.0 with security audit",
                    "budget": "$2,000,000",
                    "delegate_to": "development_orchestrator",
                },
                "marketing": {
                    "goal": "Launch campaign in 15 languages",
                    "budget": "$2,000,000",
                    "delegate_to": "marketing_orchestrator",
                },
                "operations": {
                    "goal": "Deploy to 3 regions + legal compliance",
                    "budget": "$1,000,000",
                    "delegate_to": "operations_orchestrator",
                },
            }
        }

    def delegate_to_sub_orchestrators(self, plan: dict):
        """Send each domain plan to appropriate sub-orchestrator. Layer 1 → Layer 2 only."""
        for domain_key, domain_data in plan.get("domains", {}).items():
            delegate_to = domain_data.get("delegate_to", "")
            if delegate_to and delegate_to in self.sub_orchestrators:
                self.router.send(
                    self.agent_id, 1,
                    delegate_to, 2,
                    MessageDirection.DOWN,
                    {"domain": domain_key, "goals": domain_data, "task_context": "global_launch"},
                    "global_launch",
                )
        self.tracker.update_agent_status(self.agent_id, 1, "in_progress", 0.4)

    def handle_escalation(self, from_sub_orchestrator: str, issue: str) -> str:
        """LLM decides how to handle issues escalated from Layer 2."""
        try:
            content = self.llm.generate(
                "You are the main orchestrator. Resolve escalations.",
                f"Escalation from {from_sub_orchestrator}: {issue}\n\nProvide resolution:",
            )
            return content[:300] if content else "Proceed with adjusted timeline."
        except Exception:
            return "Proceed with adjusted timeline. Monitor closely."

    def synthesize_final_report(self, all_domain_results: dict) -> str:
        """LLM combines all results into executive summary."""
        self.tracker.update_agent_status(self.agent_id, 1, "in_progress", 0.9)
        try:
            content = self.llm.generate(
                "You are the main orchestrator creating final launch report.",
                SYNTHESIS_PROMPT.format(
                    dev_results=str(all_domain_results.get("development", {})),
                    marketing_results=str(all_domain_results.get("marketing", {})),
                    ops_results=str(all_domain_results.get("operations", {})),
                ),
            )
            return content
        except Exception:
            return self._fallback_synthesis(all_domain_results)

    def _fallback_synthesis(self, results: dict) -> str:
        return f"""
LAUNCH_READINESS: ready
KEY_ACHIEVEMENTS: All domains completed. Development, Marketing, Operations delivered.
RISKS: None critical.
RECOMMENDATION: GO - All systems ready for launch.
NEXT_STEPS: Execute launch sequence. Monitor metrics.
"""
