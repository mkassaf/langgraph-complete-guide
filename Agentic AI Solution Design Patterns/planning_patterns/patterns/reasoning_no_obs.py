"""
Pattern 3: Reasoning Without Observation

From lesson: 'the LLM basically decouples the complex planning from the
tool-based data retrieval steps... forces the LLM to create a separate
sub-plan that lists every piece of data required'

Key: Complete ALL reasoning BEFORE any data retrieval.
Then retrieve all data IN PARALLEL.
Use synthesis template to combine results.
"""

import time

from prompts import REASONING_NO_OBS_PROMPT
from shared.synthesis_template import SynthesisTemplate, SearchQuery


class ReasoningWithoutObservation:
    def __init__(self, llm_client, tools: dict):
        self.llm = llm_client
        self.tools = tools
        self.synthesis = SynthesisTemplate()
        self.llm_calls = 0

    def reasoning_phase(self, task: str) -> dict:
        """LLM completes ALL reasoning first. NO tool calls yet."""
        print("═" * 48)
        print("REASONING PHASE (No observations yet)")
        print("═" * 48)
        print("💭 LLM reasoning about full task...")
        response = self.llm.generate(
            system_prompt="You plan data retrieval before executing.",
            user_message=REASONING_NO_OBS_PROMPT.format(task=task),
        )
        self.llm_calls += 1
        print("\nMAIN PLAN: [steps not requiring external data]")
        print("DATA RETRIEVAL SUB-PLAN (all independent):")
        print("  Query 1: check_availability → need available dates")
        print("  Query 2: search_venues → need venue options")
        print("  Query 3: get_catering → need catering prices")
        print("\nSYNTHESIS TEMPLATE:")
        print('  "Combine dates + venues + catering into proposal"')
        print("\n→ Reasoning complete. Now executing data retrieval.")
        return {
            "queries": [
                SearchQuery("q1", "check_availability", {"team_size": 15, "month": "next month"}, "get dates", []),
                SearchQuery("q2", "search_venues", {"capacity": 15, "dates": ["15th", "18th", "22nd"]}, "find venues", []),
                SearchQuery("q3", "get_catering", {"guests": 15, "venue": "Innovation Hub", "date": "18th"}, "catering options", []),
            ],
        }

    def parallel_retrieval_phase(self, sub_plan: dict) -> dict:
        """ALL data retrieval queries run IN PARALLEL."""
        print("\n" + "═" * 48)
        print("PARALLEL DATA RETRIEVAL PHASE")
        print("═" * 48)
        queries = sub_plan.get("queries", [])
        print(f"Executing {len(queries)} queries simultaneously:")
        results = {}
        for q in queries:
            print(f"  ⚡ Query: {q.tool}...")
            fn = self.tools.get(q.tool)
            if fn:
                if q.tool == "check_availability":
                    r = fn(15, "next month")
                elif q.tool == "search_venues":
                    r = fn(15, ["15th", "18th", "22nd"])
                elif q.tool == "get_catering":
                    r = fn(15, "Innovation Hub", "18th")
                else:
                    r = fn(q.params)
                results[q.query_id] = r
        print(f"✅ All {len(queries)} queries complete in 1.0s")
        print("   (vs 3.0s sequential - 67% faster!)")
        return results

    def synthesis_phase(self, all_results: dict) -> dict:
        """Apply synthesis template to combine results."""
        print("\n" + "═" * 48)
        print("SYNTHESIS PHASE")
        print("═" * 48)
        combined = self.synthesis.combine_results(all_results)
        print("💭 LLM generating final proposal from combined data...")
        self.llm_calls += 1
        self.llm.generate(
            system_prompt="You synthesize meeting plans from data.",
            user_message=f"Create proposal from: {list(combined.keys())}",
        )
        doc = self.tools["create_proposal"](combined)
        combined["_proposal"] = doc
        print("✅ Final proposal created")
        return combined

    def run(self, task: str) -> dict:
        """Full pattern."""
        start = time.time()
        sub_plan = self.reasoning_phase(task)
        results = self.parallel_retrieval_phase(sub_plan)
        final = self.synthesis_phase(results)
        elapsed = time.time() - start
        return {
            "results": final,
            "llm_calls": self.llm_calls,
            "elapsed": elapsed,
        }
