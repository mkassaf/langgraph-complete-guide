"""
Tool Registry — Central registry with semantic search.

Maintained by AI engineers and domain specialists.
"""

from registry.tool_spec import ToolSpec


class ToolRegistry:
    """
    Central registry of all available tools.
    Key capability: semantic search to find relevant tools
    without exposing all tools to LLM at once.
    """

    def __init__(self):
        self.tools: dict[str, ToolSpec] = {}
        self.categories: dict[str, list[str]] = {}

    def register_tool(self, spec: ToolSpec) -> None:
        """Add a tool to the registry."""
        self.tools[spec.id] = spec
        if spec.category not in self.categories:
            self.categories[spec.category] = []
        self.categories[spec.category].append(spec.id)

    def discover_tools(self, need_description: str, max_results: int = 5) -> list[ToolSpec]:
        """
        Find most relevant tools for a given need.
        Uses keyword matching against name, description, use_cases, category.
        """
        keywords = set(w.lower() for w in need_description.split() if len(w) > 2)
        scored: list[tuple[int, ToolSpec]] = []

        for spec in self.tools.values():
            score = 0
            search_text = f"{spec.name} {spec.description} {' '.join(spec.use_cases)} {spec.category}"
            search_lower = search_text.lower()
            for kw in keywords:
                if kw in search_lower:
                    score += 1
                if kw in spec.name.lower():
                    score += 2
                if kw in spec.description.lower():
                    score += 1
            if score > 0:
                scored.append((score, spec))

        scored.sort(key=lambda x: -x[0])
        return [s for _, s in scored[:max_results]]

    def get_tool_spec(self, tool_id: str) -> ToolSpec | None:
        return self.tools.get(tool_id)

    def list_categories(self) -> list[str]:
        return list(self.categories.keys())

    def get_tools_by_category(self, category: str) -> list[ToolSpec]:
        ids = self.categories.get(category, [])
        return [self.tools[i] for i in ids if i in self.tools]

    def get_registry_summary(self) -> str:
        """Brief summary for LLM - no tool details."""
        parts = [f"Registry contains {len(self.tools)} tools across {len(self.categories)} categories:"]
        for cat, ids in self.categories.items():
            parts.append(f"  {cat}({len(ids)})")
        return "\n".join(parts)
