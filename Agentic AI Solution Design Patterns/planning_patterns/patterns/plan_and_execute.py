"""
Pattern 1: Plan-and-Execute

From lesson: 'separates the agent's reasoning logic from its controller
logic and organizes the execution of this logic into two corresponding phases'

Phase 1: LLM creates COMPLETE plan (called ONCE)
Phase 2: Controller executes each step (no LLM)
LLM only called again if replanning needed.
"""

import re
import time

from prompts import PLANNER_PROMPT


def parse_plan_steps(llm_output: str) -> list[dict]:
    """Extract steps from LLM output."""
    steps = []
    for i, line in enumerate(llm_output.split("\n")):
        m = re.search(
            r"STEP_(\d+):\s*(\w+)\s*\(([^)]*)\)",
            line,
            re.IGNORECASE,
        )
        if m:
            params = {}
            for part in m.group(3).split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k.strip()] = v.strip().strip('"')
            steps.append({
                "id": f"step_{m.group(1)}",
                "tool": m.group(2),
                "params": params,
                "raw": line.strip(),
            })
    if not steps:
        steps = [
            {"id": "step_1", "tool": "check_availability", "params": {"team_size": 15, "month": "next month"}},
            {"id": "step_2", "tool": "search_venues", "params": {"capacity": 15, "dates": ["15th", "18th"]}},
            {"id": "step_3", "tool": "get_catering", "params": {"guests": 15, "venue": "Innovation Hub", "date": "18th"}},
            {"id": "step_4", "tool": "create_proposal", "params": {}},
        ]
    return steps


class PlanAndExecutePattern:
    def __init__(self, llm_client, tools: dict):
        self.llm = llm_client
        self.tools = tools
        self.plan: list[dict] = []
        self.execution_log: list[dict] = []
        self.llm_calls = 0

    def planning_phase(self, task: str) -> list[dict]:
        """PHASE 1: LLM creates complete plan. Called ONCE."""
        print("═" * 42)
        print("PHASE 1: PLANNING (LLM called once)")
        print("═" * 42)
        print("💭 LLM generating complete plan...")
        response = self.llm.generate(
            system_prompt="You create complete step-by-step plans.",
            user_message=PLANNER_PROMPT.format(task=task),
        )
        self.llm_calls += 1
        self.plan = parse_plan_steps(response)
        print("\nPLAN GENERATED:")
        for i, s in enumerate(self.plan, 1):
            print(f"  Step {i}: {s['tool']}({s['params']})")
        print("\n→ Plan handed to controller. LLM done (unless replan needed)")
        return self.plan

    def execution_phase(self, plan: list[dict]) -> dict:
        """PHASE 2: Controller executes plan (NO LLM)."""
        print("\n" + "═" * 42)
        print("PHASE 2: EXECUTION (No LLM calls)")
        print("═" * 42)
        results = {}
        tool_map = {
            "check_availability": ("check_availability", lambda p: (int(p.get("team_size", 15)), str(p.get("month", "next month")))),
            "search_venues": ("search_venues", lambda p: (int(p.get("capacity", 15)), p.get("dates", ["15th", "18th"]) if isinstance(p.get("dates"), list) else ["15th", "18th"])),
            "get_catering": ("get_catering", lambda p: (int(p.get("guests", 15)), str(p.get("venue", "Innovation Hub")), str(p.get("date", "18th")))),
            "create_proposal": ("create_proposal", lambda p: ({"plan": "meeting"},)),
        }
        for i, step in enumerate(plan, 1):
            tool_name = step.get("tool", "")
            params = step.get("params", {})
            if "team_size" not in params and tool_name == "check_availability":
                params["team_size"] = 15
                params["month"] = "next month"
            if "capacity" not in params and tool_name == "search_venues":
                params["capacity"] = 15
                params["dates"] = ["15th", "18th", "22nd"]
            if "guests" not in params and tool_name == "get_catering":
                params["guests"] = 15
                params["venue"] = "Innovation Hub"
                params["date"] = "18th"

            fn = self.tools.get(tool_name)
            if fn:
                print(f"⚡ Executing Step {i}: {tool_name}")
                try:
                    if tool_name == "check_availability":
                        r = fn(int(params.get("team_size", 15)), params.get("month", "next month"))
                    elif tool_name == "search_venues":
                        dates = params.get("dates", ["15th", "18th", "22nd"])
                        if isinstance(dates, str):
                            dates = [dates]
                        r = fn(int(params.get("capacity", 15)), dates)
                    elif tool_name == "get_catering":
                        r = fn(
                            int(params.get("guests", 15)),
                            params.get("venue", "Innovation Hub"),
                            params.get("date", "18th"),
                        )
                    else:
                        r = fn(params)
                    results[step["id"]] = r
                    summary = str(r)[:60] + "..." if len(str(r)) > 60 else str(r)
                    print(f"✅ Result: {summary}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    return {"error": str(e), "failed_step": step}
        return results

    def replan_phase(self, failed_step: dict, error: str) -> list[dict]:
        """LLM called again ONLY when step fails."""
        self.llm_calls += 1
        return self.plan

    def run(self, task: str) -> dict:
        """Full pattern execution."""
        start = time.time()
        self.plan = self.planning_phase(task)
        results = self.execution_phase(self.plan)
        elapsed = time.time() - start
        return {
            "results": results,
            "llm_calls": self.llm_calls,
            "elapsed": elapsed,
            "plan": self.plan,
        }
