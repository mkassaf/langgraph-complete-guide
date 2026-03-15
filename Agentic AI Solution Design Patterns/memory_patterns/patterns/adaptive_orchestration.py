"""
Pattern 3: Adaptive Tool Orchestration

From lesson: 'planner agent dynamically selects and coordinates an
entire toolchain based on the current plan, and then delegates this
to an orchestrator to independently carry out'

LLM role: high-level planning + toolchain definition
Orchestrator role: all tool execution (no LLM)
"""

from prompts import TOOLCHAIN_GENERATION_PROMPT


class AdaptiveToolOrchestration:
    def __init__(self, llm_client, orchestrator):
        self.llm = llm_client
        self.orchestrator = orchestrator

    def llm_generates_toolchain(
        self,
        task: str,
        context: dict | None = None,
    ) -> dict:
        """LLM creates toolchain command (high-level only)."""
        print("💭 LLM (high-level planning):")
        print('  "This task needs: calendar + venue + catering + booking"')
        print("  Generating toolchain command...")

        response = self.llm.generate(
            system_prompt="You define toolchains. Do not execute.",
            user_message=TOOLCHAIN_GENERATION_PROMPT.format(
                task=task,
                context=str(context or {}),
            ),
        )

        toolchain = {
            "chain": ["calendar_tool", "venue_tool", "catering_tool", "booking_tool"],
            "params": {
                "calendar_tool": {"team_size": 15, "weeks_ahead": 3},
                "venue_tool": {"capacity": 15},
                "catering_tool": {"guests": 15, "preference": "vegetarian"},
                "booking_tool": {"date": "18th", "guests": 15},
            },
            "sequence": "sequential",
        }
        print("\nTOOLCHAIN COMMAND:")
        print(f"  chain: {toolchain['chain']}")
        print(f"  params: {toolchain['params']}")
        print("\n→ LLM hands off to Orchestrator. LLM is done.")
        return toolchain

    def execute(self, task: str) -> dict:
        """Full orchestration flow."""
        print("\n" + "═" * 48)
        print("ADAPTIVE TOOL ORCHESTRATION")
        print("═" * 48)

        toolchain = self.llm_generates_toolchain(task, {"user": "Ahmed"})

        print("\n[ORCHESTRATOR] Taking over...")
        result = self.orchestrator.execute_toolchain(toolchain)

        print("\n✅ Consolidated result returned to controller")
        print("LLM calls during execution: 0 ✓")
        print(f"Tool calls managed by orchestrator: {len(toolchain['chain'])} ✓")
        print("\n[Note: Less adaptive - if Innovation Suite is full,")
        print(" orchestrator cannot rethink - would fail]")

        return result
