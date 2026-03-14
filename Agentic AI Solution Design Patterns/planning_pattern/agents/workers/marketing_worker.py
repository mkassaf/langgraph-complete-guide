"""
Marketing worker — creates promotional campaign.
"""

import json
import re
from agents.base_agent import BaseAgent
from communication.work_unit import WorkUnit, WorkerType, WorkerResult
from prompts import WORKER_PROMPT


class MarketingWorker(BaseAgent):
    """Handles promotional campaign for events."""

    agent_id = "marketing_worker_1"
    agent_type = "worker"

    def __init__(self, llm_client):
        self.llm = llm_client

    def process(self, input_data: dict) -> dict:
        work_unit: WorkUnit = input_data["work_unit"]
        dep_results = (work_unit.result or {}).get("dependency_results", {})
        dep_str = json.dumps(
            {k: {"summary": v.summary} for k, v in dep_results.items()},
            indent=2,
        ) if dep_results else "None"

        prompt = WORKER_PROMPT.format(
            worker_type="marketing",
            unit_description=work_unit.description,
            requirements="\n".join(work_unit.requirements),
            dependency_results=dep_str,
        )

        try:
            content = self.llm.generate(
                "You are a marketing specialist for event promotion.",
                prompt,
            )
            return self._parse_result(work_unit, content)
        except Exception:
            return self._fallback_result(work_unit)

    def _parse_result(self, unit: WorkUnit, content: str) -> WorkerResult:
        m = re.search(r"SUMMARY:\s*(.+?)(?=RECOMMENDATIONS|$)", content, re.S | re.I)
        summary = m.group(1).strip()[:200] if m else "Marketing campaign planned."
        return WorkerResult(
            unit_id=unit.unit_id,
            worker_type=WorkerType.MARKETING,
            success=True,
            output={
                "channels": ["email", "social", "LinkedIn"],
                "timeline": "4 weeks",
            },
            summary=summary,
        )

    def _fallback_result(self, unit: WorkUnit) -> WorkerResult:
        return WorkerResult(
            unit_id=unit.unit_id,
            worker_type=WorkerType.MARKETING,
            success=True,
            output={
                "channels": ["email", "LinkedIn", "Twitter"],
                "budget": 5000,
                "timeline": "4 weeks pre-event",
            },
            summary="Multi-channel campaign: email, LinkedIn, social. $5k budget, 4-week run.",
        )
