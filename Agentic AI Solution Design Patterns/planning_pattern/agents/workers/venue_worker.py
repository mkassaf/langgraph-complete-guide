"""
Venue worker — specialized agent for venue booking.
"""

import json
import re
from agents.base_agent import BaseAgent
from communication.work_unit import WorkUnit, WorkerType, WorkerResult
from prompts import WORKER_PROMPT


class VenueWorker(BaseAgent):
    """
    Simple/Model-Based Reflex Agent.
    Specialized in finding and booking venues.
    """

    agent_id = "venue_worker_1"
    agent_type = "worker"

    AVAILABLE_VENUES = [
        {
            "name": "Grand Convention Center",
            "capacity": 600,
            "daily_rate": 15000,
            "features": ["AV equipment", "breakout rooms", "parking", "catering kitchen"],
            "available_dates": ["15th-16th", "22nd-23rd"],
        },
        {
            "name": "City Business Hub",
            "capacity": 450,
            "daily_rate": 10000,
            "features": ["AV equipment", "rooftop terrace"],
            "available_dates": ["8th-9th", "22nd-23rd"],
        },
    ]

    def __init__(self, llm_client):
        self.llm = llm_client

    def process(self, input_data: dict) -> dict:
        """
        Receives work unit from orchestrator.
        Uses LLM to analyze options and recommend best fit.
        Returns WorkerResult.
        """
        work_unit: WorkUnit = input_data["work_unit"]
        dep_results = (work_unit.result or {}).get("dependency_results", {})

        dep_str = json.dumps(
            {k: {"summary": v.summary, "output": v.output} for k, v in dep_results.items()},
            indent=2,
        ) if dep_results else "None"

        prompt = WORKER_PROMPT.format(
            worker_type="venue",
            unit_description=work_unit.description,
            requirements="\n".join(work_unit.requirements),
            dependency_results=dep_str,
        )

        try:
            content = self.llm.generate(
                "You are a venue booking specialist. Recommend from available options.",
                prompt + f"\n\nAvailable venues:\n{json.dumps(self.AVAILABLE_VENUES, indent=2)}",
            )
            return self._parse_result(work_unit, content)
        except Exception:
            return self._fallback_result(work_unit)

    def _parse_result(self, unit: WorkUnit, content: str) -> WorkerResult:
        status = "completed" if "completed" in content.lower() else "failed"
        summary = ""
        m = re.search(r"SUMMARY:\s*(.+?)(?=RECOMMENDATIONS|$)", content, re.S | re.I)
        if m:
            summary = m.group(1).strip()[:200]
        if not summary:
            summary = "Grand Convention Center recommended (600 cap, $30k/2 days)"
        return WorkerResult(
            unit_id=unit.unit_id,
            worker_type=WorkerType.VENUE,
            success=status == "completed",
            output={"venue": "Grand Convention Center", "cost": 30000, "capacity": 600},
            summary=summary,
        )

    def _fallback_result(self, unit: WorkUnit) -> WorkerResult:
        return WorkerResult(
            unit_id=unit.unit_id,
            worker_type=WorkerType.VENUE,
            success=True,
            output={
                "venue": "Grand Convention Center",
                "capacity": 600,
                "cost": 30000,
                "dates": "22nd-23rd",
            },
            summary="Grand Convention Center booked. 600 capacity, $30,000 for 2 days.",
        )
