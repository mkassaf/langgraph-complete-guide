"""
Task decomposer — breaks large tasks into work units via LLM.
"""

import re
from communication.work_unit import (
    WorkUnit,
    WorkUnitStatus,
    WorkerType,
    OrchestratorPlan,
)


class TaskDecomposer:
    """
    Uses LLM to break a large task into work units.
    Core of the Planning pattern's orchestrator role.
    """

    def __init__(self, llm_client):
        self.llm = llm_client

    def decompose(
        self,
        task_description: str,
        available_workers: list[WorkerType],
    ) -> OrchestratorPlan:
        """
        LLM analyzes task and creates decomposed plan.

        Returns OrchestratorPlan with work units, assignments, dependencies.
        """
        from prompts import DECOMPOSITION_PROMPT

        prompt = DECOMPOSITION_PROMPT.format(task_description=task_description)
        try:
            content = self.llm.generate(
                "You are an orchestrator agent. Break tasks into work units.",
                prompt,
            )
            return self._parse_plan(content, task_description)
        except Exception:
            return self._fallback_plan(task_description)

    def _parse_plan(self, content: str, task: str) -> OrchestratorPlan:
        """Parse LLM output into OrchestratorPlan."""
        work_units: list[WorkUnit] = []
        execution_order: list[str] = []

        unit_blocks = re.split(r"(?=UNIT_ID:)", content, flags=re.I)
        for block in unit_blocks:
            if "UNIT_ID:" not in block.upper():
                continue
            unit_id = self._extract(r"UNIT_ID:\s*(\S+)", block)
            title = self._extract(r"TITLE:\s*(.+?)(?=ASSIGNED_TO|$)", block)
            assigned = self._extract(r"ASSIGNED_TO:\s*(\w+)", block)
            desc = self._extract(r"DESCRIPTION:\s*(.+?)(?=REQUIREMENTS|$)", block)
            reqs_raw = self._extract(r"REQUIREMENTS:\s*(.+?)(?=DEPENDS_ON|$)", block)
            deps_raw = self._extract(r"DEPENDS_ON:\s*(.+?)(?=UNIT_ID|EXECUTION_ORDER|$)", block)

            if not unit_id:
                continue

            worker = self._parse_worker_type(assigned)
            requirements = [r.strip() for r in (reqs_raw or "").split("\n") if r.strip()]
            deps = []
            if deps_raw and "none" not in (deps_raw or "").lower():
                deps = [d.strip() for d in (deps_raw or "").split(",") if d.strip()]

            work_units.append(
                WorkUnit(
                    unit_id=unit_id.strip(),
                    title=(title or unit_id).strip()[:80],
                    description=(desc or "").strip()[:500],
                    requirements=requirements[:10],
                    assigned_worker=worker,
                    dependencies=deps,
                )
            )

        exec_match = re.search(r"EXECUTION_ORDER:\s*\[?([^\]]+)\]?", content, re.I)
        if exec_match:
            execution_order = [u.strip() for u in exec_match.group(1).split(",") if u.strip()]
        if not execution_order and work_units:
            execution_order = self.determine_execution_order(work_units)

        return OrchestratorPlan(
            plan_id="plan_001",
            overall_task=task,
            work_units=work_units,
            execution_order=execution_order or [u.unit_id for u in work_units],
        )

    def _extract(self, pattern: str, text: str) -> str | None:
        m = re.search(pattern, text, re.S | re.I)
        return m.group(1).strip() if m else None

    def _parse_worker_type(self, s: str | None) -> WorkerType:
        if not s:
            return WorkerType.VENUE
        s = s.lower().replace("-", "_")
        for wt in WorkerType:
            if wt.value.replace("_", "") in s.replace("_", ""):
                return wt
        return WorkerType.VENUE

    def _fallback_plan(self, task: str) -> OrchestratorPlan:
        """Fallback plan when LLM fails."""
        return OrchestratorPlan(
            plan_id="plan_001",
            overall_task=task,
            work_units=[
                WorkUnit(
                    "unit_001",
                    "Book conference venue",
                    "Find and book venue for 500 people, 2 days",
                    ["500 capacity", "2 days", "AV equipment"],
                    WorkerType.VENUE,
                    [],
                ),
                WorkUnit(
                    "unit_002",
                    "Set up registration",
                    "Online registration system for 500 attendees",
                    ["500 capacity", "early bird pricing"],
                    WorkerType.REGISTRATION,
                    [],
                ),
                WorkUnit(
                    "unit_003",
                    "Arrange catering",
                    "Breakfast, lunch, dinner for 2 days",
                    ["500 people", "3 meals/day"],
                    WorkerType.CATERING,
                    ["unit_001"],
                ),
                WorkUnit(
                    "unit_004",
                    "Coordinate speakers",
                    "Keynote speakers for 2-day conference",
                    ["2 keynotes", "diverse topics"],
                    WorkerType.SPEAKERS,
                    ["unit_001"],
                ),
                WorkUnit(
                    "unit_005",
                    "Marketing campaign",
                    "Promotional campaign for conference",
                    ["500 target", "multi-channel"],
                    WorkerType.MARKETING,
                    ["unit_002"],
                ),
            ],
            execution_order=["unit_001", "unit_002", "unit_003", "unit_004", "unit_005"],
        )

    def determine_execution_order(self, work_units: list[WorkUnit]) -> list[str]:
        """
        Topological sort of work units based on dependencies.
        """
        unit_ids = {u.unit_id for u in work_units}
        deps_map = {u.unit_id: [d for d in u.dependencies if d in unit_ids] for u in work_units}
        order: list[str] = []
        visited = set()

        def visit(uid: str):
            if uid in visited:
                return
            visited.add(uid)
            for d in deps_map.get(uid, []):
                visit(d)
            order.append(uid)

        for u in work_units:
            visit(u.unit_id)

        return order
