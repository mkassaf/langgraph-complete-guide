"""
Pattern 1: Language Agent Tree Search (LATS)

From lesson: 'integrate the LLM's reasoning capabilities with an advanced
search algorithm... a variant of the Monte Carlo Tree Search algorithm'

Generates MULTIPLE candidate actions, evaluates via MCTS, selects best atomic action.
"""

import re
from shared.mcts_tree import MCTSTree, MCTSNode
from prompts import LATS_GENERATE_ACTIONS_PROMPT, LATS_EVALUATE_PROMPT


def parse_actions(llm_output: str) -> list[dict]:
    """Extract ACTION_A, B, C from LLM output."""
    actions = []
    for block in ["ACTION_A", "ACTION_B", "ACTION_C"]:
        m = re.search(
            rf"{block}:?\s*action:\s*(.+?)(?=thought:|$)",
            llm_output,
            re.DOTALL | re.IGNORECASE,
        )
        if m:
            action = m.group(1).strip()[:80]
        else:
            action = f"{block} default"
        thought_m = re.search(
            rf"{block}:?.*?thought:\s*(.+?)(?=predicted|$)",
            llm_output,
            re.DOTALL | re.IGNORECASE,
        )
        thought = thought_m.group(1).strip()[:100] if thought_m else ""
        pred_m = re.search(
            rf"{block}:?.*?predicted_success:\s*([0-9.]+)",
            llm_output,
            re.IGNORECASE,
        )
        pred = float(pred_m.group(1)) if pred_m else 0.5
        actions.append({"action": action, "thought": thought, "predicted": pred})
    if not actions:
        actions = [
            {"action": "check_availability first", "thought": "Confirm dates", "predicted": 0.85},
            {"action": "search_venues first", "thought": "Find space", "predicted": 0.45},
            {"action": "check_budget first", "thought": "Verify funds", "predicted": 0.65},
        ]
    return actions


def parse_score(llm_output: str) -> float:
    m = re.search(r"SUCCESS_PROBABILITY:\s*([0-9.]+)", llm_output, re.IGNORECASE)
    return float(m.group(1)) if m else 0.6


class LATSPattern:
    def __init__(self, llm_client, tools: dict, mcts_iterations: int = 5):
        self.llm = llm_client
        self.tools = tools
        self.iterations = mcts_iterations

    def generate_candidate_actions(self, current_state: str, task: str) -> list[dict]:
        """LLM proposes multiple diverse next steps."""
        response = self.llm.generate(
            system_prompt="You propose diverse planning actions.",
            user_message=LATS_GENERATE_ACTIONS_PROMPT.format(
                task=task, state=current_state
            ),
        )
        return parse_actions(response)

    def evaluate_action(self, action: str, context: str) -> tuple[float, str]:
        """LLM scores a hypothetical action."""
        response = self.llm.generate(
            system_prompt="You evaluate planning actions.",
            user_message=LATS_EVALUATE_PROMPT.format(action=action, context=context),
        )
        return parse_score(response), response[:150]

    def run_mcts_loop(self, task: str, num_steps: int = 4) -> list[str]:
        """Full LATS: run MCTS → get atomic action → execute per step."""
        executed = []
        state = "Initial state"

        for step_num in range(1, min(num_steps, 4) + 1):
            print("\n" + "═" * 42)
            print(f"LATS STEP {step_num}: Finding best action")
            print("═" * 42)
            print(f"Running {self.iterations} MCTS iterations...")

            tree = MCTSTree(task)

            for it in range(self.iterations):
                print(f"\n  Iteration {it + 1}:")
                node = tree.selection_phase()

                if not node.children and node.action == "start":
                    actions = self.generate_candidate_actions(state, task)
                    new_nodes = tree.expansion_phase(node, actions)
                    node = new_nodes[it % len(new_nodes)] if new_nodes else node

                elif node.parent_id and node.visit_count == 0:
                    pass

                if node.action != "start":
                    score, reasoning = self.evaluate_action(node.action, state)
                    tree.simulation_phase(node, score, reasoning)
                    tree.backpropagation_phase(node, score)

            best = tree.get_best_action()
            if best:
                print(f"\n⚡ ATOMIC ACTION: \"{best.action}\" (score: {best.average_score:.2f})")
                print("   → Executing...")
                executed.append(best.action)
                if "check_availability" in best.action.lower() or "availability" in best.action.lower():
                    r = self.tools["check_availability"](15, 3)
                    state = f"Dates: {r.get('available_dates', [])}"
                elif "search_venues" in best.action.lower() or "venue" in best.action.lower():
                    r = self.tools["search_venues"](15, ["15th", "18th", "22nd"])
                    state = f"Venues: {[v['name'] for v in r.get('venues', [])]}"
                elif "catering" in best.action.lower():
                    r = self.tools["get_catering"](15, "Innovation Hub", "18th")
                    state = f"Catering: {[o['provider'] for o in r.get('options', [])]}"
                else:
                    state = f"Completed: {best.action}"
                print(f"   ✅ Result: {state[:60]}...")

        return executed

    def run(self, task: str) -> dict:
        executed = self.run_mcts_loop(task)
        return {"executed_actions": executed, "task": task}
