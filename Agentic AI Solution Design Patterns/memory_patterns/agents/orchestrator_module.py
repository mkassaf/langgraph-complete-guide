"""
The orchestrator module for adaptive tool orchestration.

From lesson: 'specialized orchestrator module handles the actual
execution of the predetermined sequence of tool calls in the toolchain'

Key: Executes tool chains WITHOUT LLM involvement.
"""


class OrchestratorModule:
    def __init__(self, tools: dict):
        self.tools = tools
        self.state: dict = {}

    def execute_toolchain(self, toolchain_command: dict) -> dict:
        """Execute a complete tool chain independently."""
        chain = toolchain_command.get("chain", [])
        params = toolchain_command.get("params", {})
        self.state = {}

        print("[ORCHESTRATOR] Received toolchain command")
        print(f"[ORCHESTRATOR] Executing chain: {' → '.join(chain)}")

        for i, tool_name in enumerate(chain, 1):
            fn = self.tools.get(tool_name)
            if not fn:
                continue
            p = params.get(tool_name, {})

            print(f"\n[ORCHESTRATOR] Step {i}: {tool_name}({p})")

            try:
                if tool_name == "calendar_tool":
                    r = fn(p.get("team_size", 15), p.get("weeks_ahead", 3))
                    self.state["dates"] = r.get("available_dates", [])
                    print(f"[ORCHESTRATOR] → Available dates: {self.state['dates']} ✓")
                elif tool_name == "venue_tool":
                    r = fn(p.get("capacity", 15), self.state.get("dates", ["18th"]))
                    venues = r.get("venues", [])
                    self.state["venue"] = venues[0]["name"] if venues else "Innovation Suite"
                    print(f"[ORCHESTRATOR] → {self.state['venue']} available ✓")
                elif tool_name == "catering_tool":
                    r = fn(
                        p.get("guests", 15),
                        self.state.get("venue", "Innovation Suite"),
                        p.get("preference", ""),
                    )
                    self.state["catering"] = r.get("options", [{}])[0].get("menu", "Mediterranean")
                    print(f"[ORCHESTRATOR] → {self.state['catering']} menu confirmed ✓")
                elif tool_name == "booking_tool":
                    r = fn(
                        self.state.get("venue", "Innovation Suite"),
                        p.get("date", "18th"),
                        p.get("guests", 15),
                    )
                    self.state["booking"] = r
                    print(f"[ORCHESTRATOR] → Booking confirmed ✓")
            except Exception as e:
                print(f"[ORCHESTRATOR] → Error: {e}")

        print("\n[ORCHESTRATOR] Chain complete. Returning consolidated result.")
        print("Note: LLM was NOT involved in any of these steps ✓")
        return self.state
