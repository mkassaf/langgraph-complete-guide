"""
Pattern 4: Planner-Critic-Refiner

From lesson: 'establishes a feedback loop between the planner agent and
a separate critic agent, whereby the critic agent contains logic capable
of assessing a proposed plan. It then provides its feedback to the planner
agent so that it can refine the plan.'

Three roles: PLANNER, CRITIC, REFINER (same LLM, different prompts)
"""

import re
import time

from prompts import PLANNER_PROMPT, CRITIC_PROMPT, REFINER_PROMPT
from .plan_and_execute import parse_plan_steps


def parse_quality_score(text: str) -> float:
    m = re.search(r"QUALITY_SCORE:\s*([0-9.]+)", text, re.IGNORECASE)
    return float(m.group(1)) if m else 0.5


def parse_approved(text: str) -> bool:
    return "APPROVED: yes" in text.upper() or "APPROVED:yes" in text.upper()


class PlannerCriticRefiner:
    def __init__(
        self,
        llm_client,
        tools: dict,
        max_iterations: int = 3,
        quality_threshold: float = 0.85,
        demo_scores: list[float] | None = None,
    ):
        self.llm = llm_client
        self.tools = tools
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        self.demo_scores = demo_scores or []
        self.llm_calls = 0

    def planner_role(self, task: str) -> dict:
        """LLM in PLANNER role creates initial plan."""
        response = self.llm.generate(
            system_prompt="You are a meeting planning PLANNER.",
            user_message=PLANNER_PROMPT.format(task=task),
        )
        self.llm_calls += 1
        steps = parse_plan_steps(response)
        return {"steps": steps, "raw": response}

    def critic_role(self, plan: dict, iteration: int = 0) -> dict:
        """LLM in CRITIC role evaluates plan."""
        response = self.llm.generate(
            system_prompt="You are a CRITIC evaluating meeting plans.",
            user_message=CRITIC_PROMPT.format(plan=str(plan)),
        )
        self.llm_calls += 1
        if self.demo_scores and iteration < len(self.demo_scores):
            score = self.demo_scores[iteration]
        else:
            score = parse_quality_score(response)
        approved = parse_approved(response) or score >= self.quality_threshold
        issues = []
        for line in response.split("\n"):
            if "ISSUE:" in line or "⚠" in line or "issue" in line.lower():
                issues.append(line.strip())
        return {
            "feedback": response,
            "quality_score": score,
            "approved": approved,
            "issues": issues[:5],
        }

    def refiner_role(self, original_plan: dict, critic_feedback: dict) -> dict:
        """Planner assumes REFINER role. Incorporates critic feedback."""
        response = self.llm.generate(
            system_prompt="You are a REFINER improving plans.",
            user_message=REFINER_PROMPT.format(
                plan=str(original_plan),
                feedback=critic_feedback.get("feedback", ""),
            ),
        )
        self.llm_calls += 1
        steps = parse_plan_steps(response)
        if not steps:
            steps = original_plan.get("steps", [])
        return {"steps": steps, "raw": response}

    def run(self, task: str) -> dict:
        """Full critique loop."""
        start = time.time()
        plan = self.planner_role(task)

        for iteration in range(1, self.max_iterations + 1):
            print("\n" + "═" * 42)
            print(f"ITERATION {iteration}")
            print("═" * 42)
            print("📋 PLANNER generated plan" if iteration == 1 else "✏️  REFINER updated plan")

            print("\n🔍 CRITIC evaluating plan...")
            critique = self.critic_role(plan, iteration - 1)

            if critique.get("issues"):
                print("Issues found:")
                for iss in critique["issues"][:3]:
                    print(f"  ⚠️  {iss[:70]}...")
            print(f"Quality score: {critique['quality_score']:.2f} (threshold {self.quality_threshold})")

            if critique.get("approved"):
                print("✅ Plan approved! Proceeding to execution.")
                break

            print("\n✏️  REFINER incorporating feedback...")
            plan = self.refiner_role(plan, critique)
            plan["steps"] = plan.get("steps", [])

        results = {}
        for step in plan.get("steps", []):
            fn = self.tools.get(step.get("tool", ""))
            if fn:
                try:
                    if step["tool"] == "check_availability":
                        results[step["id"]] = fn(15, "next month")
                    elif step["tool"] == "search_venues":
                        results[step["id"]] = fn(15, ["15th", "18th", "22nd"])
                    elif step["tool"] == "get_catering":
                        results[step["id"]] = fn(15, "Innovation Hub", "18th")
                    else:
                        results[step["id"]] = fn(results)
                except Exception:
                    pass

        elapsed = time.time() - start
        return {
            "results": results,
            "llm_calls": self.llm_calls,
            "elapsed": elapsed,
            "plan": plan,
            "iterations": iteration,
        }
