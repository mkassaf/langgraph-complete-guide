"""
Graph Query Tool — Tool for agents to query the knowledge graph.

Used as an ACTION in the ReAct pattern.
"""

from dataclasses import dataclass

from graph.knowledge_graph import Entity, EntityType, KnowledgeGraph, RelationType


@dataclass
class QueryResult:
    query: str
    found: bool
    entities: list[Entity]
    relationships: list
    context_string: str


class GraphQueryTool:
    """Tool that agents use to query the knowledge graph."""

    name = "graph_query_tool"

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def execute(self, query: str) -> QueryResult:
        """Natural language query interface."""
        q = query.lower()
        entities = []
        context_parts = []

        # "where is the printer?"
        if "printer" in q and ("where" in q or "location" in q or "located" in q):
            r = self.graph.query("printer")
            if r.get("entity"):
                entities.append(r["entity"])
                context_parts.append(self.graph.to_context_string(r))

        # "what equipment is in room 303?"
        elif "room 303" in q or "room303" in q:
            for rel in self.graph.relationships:
                if rel.to_entity == "room_303" and rel.relation == RelationType.LOCATED_IN:
                    ent = self.graph.entities.get(rel.from_entity)
                    if ent:
                        entities.append(ent)
                        r = self.graph.query(ent.name)
                        context_parts.append(self.graph.to_context_string(r))

        # "who manages" / "who should I contact"
        elif "who" in q and ("manage" in q or "contact" in q or "printer" in q):
            for rel in self.graph.relationships:
                if rel.to_entity == "printer" and rel.relation == RelationType.MANAGES:
                    ent = self.graph.entities.get(rel.from_entity)
                    if ent:
                        entities.append(ent)
                        r = self.graph.query(ent.name)
                        context_parts.append(self.graph.to_context_string(r))
            if not entities:
                r = self.graph.query("printer")
                if r.get("entity"):
                    context_parts.append(self.graph.to_context_string(r))

        # "what paper does the printer use"
        elif "paper" in q or "supply" in q:
            r = self.graph.query("printer")
            if r.get("entity"):
                context_parts.append(self.graph.to_context_string(r))
            r2 = self.graph.query("A4 Paper")
            if r2.get("entity"):
                context_parts.append(self.graph.to_context_string(r2))

        # "path from printer to paper"
        elif "path" in q or "get from" in q or "how do i get" in q:
            path = self.graph.find_path("printer", "supply")
            if path:
                context_parts.append(f"Path from Printer to Paper Supply: {' → '.join(path)}")
            else:
                r = self.graph.query("printer")
                r2 = self.graph.query("Supply Room A")
                context_parts.append(self.graph.to_context_string(r))
                if r2.get("entity"):
                    context_parts.append(self.graph.to_context_string(r2))

        # Fallback: try entity name from query
        else:
            for eid, ent in self.graph.entities.items():
                if any(w in q for w in ent.name.lower().split()):
                    r = self.graph.query(ent.name)
                    context_parts.append(self.graph.to_context_string(r))
                    entities.append(ent)
                    break

        context_string = "\n\n".join(context_parts) if context_parts else "No matching data found."
        return QueryResult(
            query=query,
            found=bool(context_parts),
            entities=entities,
            relationships=[],
            context_string=context_string,
        )

    def query_entity(self, entity_name: str) -> QueryResult:
        """Direct entity lookup."""
        r = self.graph.query(entity_name)
        return QueryResult(
            query=entity_name,
            found=r.get("entity") is not None,
            entities=[r["entity"]] if r.get("entity") else [],
            relationships=[],
            context_string=self.graph.to_context_string(r),
        )
