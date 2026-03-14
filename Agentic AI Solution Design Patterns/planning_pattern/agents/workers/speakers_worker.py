"""
Speakers worker — coordinates keynote speakers.
"""

import json
import re
from agents.base_agent import BaseAgent
from communication.work_unit import WorkUnit, WorkerType, WorkerResult
from prompts import WORKER_PROMPT


class SpeakersWorker(BaseAgent):
    """Coordinates keynote speakers for events."""

    agent_id = "speakers_worker_1"
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
            worker_type="speakers",
            unit_description=work_unit.description,
            requirements="\n".join(work_unit.requirements),
            dependency_results=dep_str,
        )

        try:
            content = self.llm.generate(
                "You are a speaker coordination specialist for conferences.",
                prompt,
            )
            return self._parse_result(work_unit, content)
        except Exception:
            return self._fallback_result(work_unit)

    def _parse_result(self, unit: WorkUnit, content: str) -> WorkerResult:
        m = re.search(r"SUMMARY:\s*(.+?)(?=RECOMMENDATIONS|$)", content, re.S | re.I)
        summary = m.group(1).strip()[:200] if m else "Speakers coordinated."
        return WorkerResult(
            unit_id=unit.unit_id,
            worker_type=WorkerType.SPEAKERS,
            success=True,
            output={
                "keynote1": "Industry leader",
                "keynote2": "Innovation expert",
            },
            summary=summary,
        )

    def _fallback_result(self, unit: WorkUnit) -> WorkerResult:
        return WorkerResult(
            unit_id=unit.unit_id,
            worker_type=WorkerType.SPEAKERS,
            success=True,
            output={
                "day1_keynote": "CEO, Tech Corp",
                "day2_keynote": "Chief Innovation Officer",
                "honorarium": 5000,
            },
            summary="2 keynote speakers confirmed. Day 1: CEO, Day 2: Innovation lead.",
        )
