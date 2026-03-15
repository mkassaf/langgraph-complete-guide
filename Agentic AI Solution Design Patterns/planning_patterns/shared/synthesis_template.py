"""
Synthesis template for combining parallel search results.

From lesson: 'a synthesis template... a component used by the agent
to provide the instructions for how to combine the concurrently
fetched data into the final output'

Used for independent search/retrieval queries.
"""

from dataclasses import dataclass, field


@dataclass
class SearchQuery:
    query_id: str
    tool: str
    params: dict
    purpose: str
    independent_of: list = field(default_factory=list)


class SynthesisTemplate:
    def __init__(self):
        self.queries: list[SearchQuery] = []
        self.combination_logic: str = ""
        self.output_format: str = ""

    def add_query(self, query: SearchQuery):
        self.queries.append(query)

    def combine_results(self, results: dict[str, dict]) -> dict:
        """Merge all parallel query results per template logic."""
        n = len(results)
        print(f"[SYNTHESIS] Combining {n} parallel results...")
        combined = {"_sources": list(results.keys()), **results}
        return combined
