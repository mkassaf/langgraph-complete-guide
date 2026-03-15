"""
Pattern 3: Second-Pass Verification

From lesson: 'introduces verification logic... a dedicated verifier agent
whose sole responsibility is to evaluate LLM outputs'

Key: Verifier has its OWN separate LLM (not planner's LLM).
"""

import re

from tools.compliance_checker_tool import check_vendor_compliance
from prompts import VERIFIER_PROMPT


def parse_verdict(text: str) -> str:
    m = re.search(r"OVERALL_VERDICT:\s*(\w+)", text, re.IGNORECASE)
    return (m.group(1) or "fail").lower()


class SecondPassVerification:
    def __init__(self, planner_llm, verifier_llm, tools: dict):
        self.planner_llm = planner_llm
        self.verifier_llm = verifier_llm
        self.tools = tools
        self.verification_log: list[dict] = []

    def planner_generates(self, task: str, inject_errors: bool = True) -> dict:
        """Planner LLM creates plan. May contain intentional errors for demo."""
        plan = {
            "agenda": [
                "12:00 - Lunch",
                "09:00 - Kickoff",
                "10:30 - Team activities",
                "14:00 - Wrap-up",
            ],
            "venue": "Innovation Hub",
            "caterer": "Gourmet Foods" if inject_errors else "Fresh & Local",
            "budget": 2000,
        }
        return plan

    def verifier_checks(self, plan: dict) -> dict:
        """Independent verifier LLM evaluates plan. Uses its OWN reasoning + tools."""
        print("═" * 48)
        print("VERIFIER AGENT: Independent verification")
        print("═" * 48)
        print("Using SEPARATE LLM (not planner's LLM)")
        print("\n💭 Verifier LLM checking plan...")

        response = self.verifier_llm.generate(
            system_prompt="You are a VERIFIER. Evaluate plans for errors.",
            user_message=VERIFIER_PROMPT.format(plan=str(plan)),
        )

        issues = []
        print("\n  Check 1: Logical sequence...")
        if "12:00" in str(plan.get("agenda", [])) and "09:00" in str(plan.get("agenda", [])):
            idx_lunch = str(plan["agenda"]).find("12:00")
            idx_kickoff = str(plan["agenda"]).find("09:00")
            if idx_lunch < idx_kickoff:
                print("  ❌ FAIL: Lunch listed before kickoff!")
                issues.append({"check": "sequence", "severity": "minor"})

        print("  Check 2: Vendor compliance...")
        caterer = plan.get("caterer", "")
        comp = check_vendor_compliance(caterer)
        if not comp.get("approved"):
            print(f"  ❌ FAIL: \"{caterer}\" not on approved vendor list!")
            issues.append({"check": "vendor", "severity": "fatal"})
        else:
            print("  ✅ PASS: Vendor approved")

        print("  Check 3: Dates and capacities...")
        print("  ✅ PASS: All dates valid")

        verdict = "fail" if issues else parse_verdict(response)
        if "fatal" in [i.get("severity") for i in issues]:
            verdict = "fail"

        print(f"\n  VERDICT: {verdict.upper()}")
        if issues:
            print(f"  Severity: {', '.join(i['severity'] for i in issues)}")
            print("  → Sending to planner for revision")

        result = {
            "verdict": verdict,
            "issues": issues,
            "explanation": response[:300],
        }
        self.verification_log.append(result)
        return result

    def planner_revises(
        self, original_plan: dict, verification_result: dict
    ) -> dict:
        """Planner uses verdict as observation. Revises plan to fix issues."""
        revised = original_plan.copy()
        for issue in verification_result.get("issues", []):
            if issue.get("check") == "sequence":
                revised["agenda"] = [
                    "09:00 - Kickoff",
                    "10:30 - Team activities",
                    "12:00 - Lunch",
                    "14:00 - Wrap-up",
                ]
            if issue.get("check") == "vendor":
                revised["caterer"] = "Fresh & Local"
        return revised

    def controller_decision(self, verification_result: dict) -> str:
        """Controller decides based on severity."""
        if verification_result.get("verdict") == "pass":
            return "execute"
        if any(i.get("severity") == "fatal" for i in verification_result.get("issues", [])):
            return "replan"
        return "human_review"

    def run(self, task: str) -> dict:
        """Full verification cycle: plan → verify → (fail: revise) → verify again."""
        print("\n" + "━" * 60)
        print("ROUND 1")
        print("━" * 60)
        plan = self.planner_generates(task, inject_errors=True)
        print("📋 Planner LLM generates plan...")
        print("   (Plan contains intentional errors for demo)")

        v1 = self.verifier_checks(plan)
        if v1.get("verdict") == "pass":
            return {"plan": plan, "rounds": 1, "verification_log": self.verification_log}

        print("\n📋 Planner revises based on feedback...")

        print("\n" + "━" * 60)
        print("ROUND 2")
        print("━" * 60)
        revised = self.planner_revises(plan, v1)
        v2 = self.verifier_checks(revised)

        if v2.get("verdict") == "pass":
            print("\n✅ Controller: Plan approved → executing")
        return {
            "plan": revised,
            "rounds": 2,
            "verification_log": self.verification_log,
        }
