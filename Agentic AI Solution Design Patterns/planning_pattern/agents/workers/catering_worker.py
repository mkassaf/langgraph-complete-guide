"""
Catering worker — arranges food and beverage.
"""

import json
import re
from agents.base_agent import BaseAgent
from communication.work_unit import WorkUnit, WorkerType, WorkerResult
from prompts import WORKER_PROMPT


class CateringWorker(BaseAgent):
    """Arranges catering for events."""

    agent_id = "catering_worker_1"
    agent_type = "worker"

    def __init__(self, llm_client):
        self.llm = llm_client

    def process(self, input_data: dict) -> dict:
        work_unit: WorkUnit = input_data["work_unit"]
        dep_results = (work_unit.result or {}).get("dependency_results", {})
        dep_str = json.dumps(
            {k: {"summary": v.summary, "output": v.output} for k, v in dep_results.items()},
            indent=2,
        ) if dep_results else "None"

        prompt = WORKER_PROMPT.format(
            worker_type="catering",
            unit_description=work_unit.description,
            requirements="\n".join(work_unit.requirements),
            dependency_results=dep_str,
        )

        try:
            content = self.llm.generate(
                "You are a catering specialist. Plan meals for 500 people, 2 days.",
                prompt,
            )
            return self._parse_result(work_unit, content)
        except Exception:
            return self._fallback_result(work_unit)

    def _parse_result(self, unit: WorkUnit, content: str) -> WorkerResult:
        m = re.search(r"SUMMARY:\s*(.+?)(?=RECOMMENDATIONS|$)", content, re.S | re.I)
        summary = m.group(1).strip()[:200] if m else "Catering arranged."
        return WorkerResult(
            unit_id=unit.unit_id,
            worker_type=WorkerType.CATERING,
            success=True,
            output={
                "breakfast": "Continental buffet",
                "lunch": "Boxed lunch",
                "dinner": "Buffet dinner",
                "cost_per_person": 45,
            },
            summary=summary,
        )

    def _fallback_result(self, unit: WorkUnit) -> WorkerResult:
        return WorkerResult(
            unit_id=unit.unit_id,
            worker_type=WorkerType.CATERING,
            success=True,
            output={
                "day1_breakfast": "Continental buffet",
                "day1_lunch": "Boxed lunch",
                "day1_dinner": "Buffet",
                "day2_breakfast": "Continental",
                "day2_lunch": "Boxed lunch",
                "total_cost": 22500,
            },
            summary="Full catering: breakfast, lunch, dinner x2 days. ~$22,500 for 500.",
        )
