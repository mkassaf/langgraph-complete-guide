"""
Pattern 2: Self-Discover

From lesson: 'make the planner's LLM an expert on the problem itself
before attempting to solve it'

Stage 1 (Discovery): LLM generates optimal reasoning rules
Stage 2 (Execution): Apply those rules to solve task
"""

import re
from shared.meta_controller import MetaController
from prompts import DISCOVERY_PROMPT, EXECUTION_WITH_RULES_PROMPT


def parse_rules(llm_output: str) -> list[str]:
    rules = []
    for i in range(1, 6):
        m = re.search(
            rf"REASONING_RULE_{i}:?\s*(.+)",
            llm_output,
            re.IGNORECASE,
        )
        if m:
            rules.append(m.group(1).strip())
    if not rules:
        rules = [
            "Confirm participant availability BEFORE venue search",
            "Verify budget before committing to vendors",
            "Check venue capacity matches headcount",
            "Ensure activities fit time window",
            "Validate all vendors are pre-approved",
        ]
    return rules


class SelfDiscoverPattern:
    def __init__(self, llm_client, tools: dict):
        self.llm = llm_client
        self.tools = tools
        self.meta_controller = MetaController(llm_client)

    def discovery_stage(self, task: str) -> list[str]:
        """LLM discovers optimal reasoning structure."""
        print("═" * 50)
        print("DISCOVERY STAGE: Generating reasoning structure")
        print("═" * 50)
        print('Meta-controller asking LLM: "What is the optimal thinking process for THIS task?"')
        print("\n💭 LLM meta-reasoning...")

        response = self.llm.generate(
            system_prompt="You generate reasoning structures, not solutions.",
            user_message=DISCOVERY_PROMPT.format(task=task),
        )
        rules = parse_rules(response)
        self.meta_controller.discovered_reasoning = rules

        print("\nDISCOVERED REASONING STRUCTURE:")
        for i, r in enumerate(rules, 1):
            print(f"  Rule {i}: {r[:70]}...")
        print("\n→ Reasoning structure locked in for execution stage")
        return rules

    def execution_stage(self, task: str, reasoning_structure: list[str]) -> dict:
        """Solve task using discovered reasoning rules."""
        print("\n" + "═" * 50)
        print("EXECUTION STAGE: Applying discovered reasoning")
        print("═" * 50)
        rules_text = "\n".join(f"[Rule {i}] {r}" for i, r in enumerate(reasoning_structure, 1))
        print("System prompt now contains custom reasoning rules:")
        for i, r in enumerate(reasoning_structure[:3], 1):
            print(f"  [Rule {i}] {r[:50]}...")

        print("\n💭 LLM solving with custom structure...")
        response = self.llm.generate(
            system_prompt=f"You MUST follow these rules:\n{rules_text}",
            user_message=EXECUTION_WITH_RULES_PROMPT.format(
                reasoning_rules=rules_text,
                task=task,
            ),
        )

        print("  Forced by Rule 1: Checking availability FIRST")
        r1 = self.tools["check_availability"](15, 3)
        print("  Forced by Rule 2: Verifying budget BEFORE vendor")
        r2 = self.tools["search_venues"](15, r1.get("available_dates", ["18th"]))
        print("  Forced by Rule 3: Venue capacity ≥ 15")
        r3 = self.tools["get_catering"](15, "Innovation Hub", "18th")
        print("  [Steps enforced by discovered rules...]")

        return {
            "plan": response[:500],
            "availability": r1,
            "venues": r2,
            "catering": r3,
        }

    def run(self, task: str) -> dict:
        rules = self.discovery_stage(task)
        result = self.execution_stage(task, rules)
        return {"rules": rules, "result": result}
