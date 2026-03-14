"""
Orchestrator agent — goal-based planner and coordinator.
"""

from communication.work_unit import (
    WorkUnit,
    WorkUnitStatus,
    WorkerType,
    OrchestratorPlan,
    WorkerResult,
)
from communication.message_bus import MessageBus
from agents.orchestrator.task_decomposer import TaskDecomposer
from agents.base_agent import BaseAgent
from prompts import SYNTHESIS_PROMPT


class OrchestratorAgent(BaseAgent):
    """
    Goal-based agent that plans and coordinates.

    Responsibilities:
    1. Receive large complex task
    2. Use LLM to decompose into work units
    3. Delegate work units to worker agents
    4. Monitor worker progress
    5. Aggregate results into final output
    """

    def __init__(self, llm_client, message_bus: MessageBus):
        self.llm = llm_client
        self.bus = message_bus
        self.decomposer = TaskDecomposer(llm_client)
        self.agent_id = "orchestrator_1"
        self.agent_type = "orchestrator"
        self.active_plan: OrchestratorPlan | None = None
        self.completed_units: dict[str, WorkerResult] = {}

    def process(self, input_data: dict) -> dict:
        """
        Full orchestration flow:
        1. Decompose task into plan
        2. Execute work units in dependency order
        3. Collect all worker results
        4. Synthesize final plan
        """
        task = input_data.get("task", "")
        self.completed_units = {}

        plan = self.decomposer.decompose(task, list(WorkerType))
        self.active_plan = plan

        results: dict[str, WorkerResult] = {}
        for unit_id in plan.execution_order:
            unit = next((u for u in plan.work_units if u.unit_id == unit_id), None)
            if not unit:
                continue
            deps_ready = all(d in results for d in unit.dependencies)
            if not deps_ready:
                continue

            dep_results = {d: results[d] for d in unit.dependencies if d in results}
            unit.result = {"dependency_results": dep_results}
            result = self.delegate_work_unit(unit, dep_results)
            results[unit_id] = result
            self.completed_units[unit_id] = result

        synthesis = self.synthesize_results(results)
        return {
            "plan": plan,
            "results": results,
            "synthesis": synthesis,
        }

    def delegate_work_unit(
        self,
        unit: WorkUnit,
        dependency_results: dict[str, WorkerResult] | None = None,
    ) -> WorkerResult:
        """
        Send work unit to appropriate worker via message bus.
        Pass dependency context to worker.
        """
        unit.result = unit.result or {}
        unit.result["dependency_results"] = dependency_results or {}
        return self.bus.send_to_worker(unit, self.agent_id)

    def synthesize_results(self, results: dict[str, WorkerResult]) -> str:
        """
        LLM combines all worker results into coherent final plan.
        """
        lines = []
        for uid, r in results.items():
            lines.append(f"Unit {uid} ({r.worker_type.value}): success={r.success}")
            lines.append(f"  Summary: {r.summary}")
            lines.append(f"  Output: {r.output}")
        all_results_str = "\n".join(lines)

        prompt = SYNTHESIS_PROMPT.format(all_results=all_results_str)
        try:
            return self.llm.generate(
                "You are an orchestrator synthesizing worker results into a final plan.",
                prompt,
            )
        except Exception:
            return self._fallback_synthesis(results)

    def _fallback_synthesis(self, results: dict[str, WorkerResult]) -> str:
        """Fallback when LLM fails."""
        parts = ["FINAL CONFERENCE PLAN (synthesized from worker results)\n"]
        for uid, r in results.items():
            parts.append(f"- {uid}: {r.summary}")
        return "\n".join(parts)

    def handle_worker_failure(self, unit: WorkUnit, error: str) -> WorkerResult:
        """
        If worker fails, orchestrator decides next steps.
        """
        return WorkerResult(
            unit_id=unit.unit_id,
            worker_type=unit.assigned_worker,
            success=False,
            output={"error": error},
            summary=f"Failed: {error}",
        )
