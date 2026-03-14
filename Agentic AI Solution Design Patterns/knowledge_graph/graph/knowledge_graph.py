"""
Knowledge Graph — Core data structure

Stores office building entities and relationships.
Prevents LLM hallucinations by providing accurate, up-to-date information.
"""

from collections import deque
from dataclasses import dataclass, field
from enum import Enum


class EntityType(Enum):
    ROOM = "room"
    EQUIPMENT = "equipment"
    PERSON = "person"
    SUPPLY = "supply"
    DEPARTMENT = "department"


class RelationType(Enum):
    LOCATED_IN = "located_in"
    USES = "uses"
    WORKS_IN = "works_in"
    MANAGES = "manages"
    CONNECTED_TO = "connected_to"
    REQUIRES = "requires"
    AVAILABLE_IN = "available_in"


@dataclass
class Entity:
    id: str
    name: str
    type: EntityType
    properties: dict = field(default_factory=dict)
    last_updated: str = ""


@dataclass
class Relationship:
    from_entity: str
    relation: RelationType
    to_entity: str
    properties: dict = field(default_factory=dict)


class KnowledgeGraph:
    """
    Stores office building entities and their relationships.
    Prevents LLM hallucinations by providing accurate, up-to-date information.
    """

    def __init__(self):
        self.entities: dict[str, Entity] = {}
        self.relationships: list[Relationship] = []

    def add_entity(self, entity: Entity) -> None:
        """Add or update an entity in the graph."""
        self.entities[entity.id] = entity

    def add_relationship(self, rel: Relationship) -> None:
        """Add a relationship between entities."""
        self.relationships.append(rel)

    def query(self, entity_name: str) -> dict:
        """
        Find all information about an entity:
        - Its properties
        - All relationships it has
        - Related entities and their properties
        """
        entity_name_lower = entity_name.lower()
        result = {"entity": None, "outgoing": [], "incoming": [], "related_entities": {}}

        for eid, ent in self.entities.items():
            if entity_name_lower in ent.name.lower() or entity_name_lower in eid.lower():
                result["entity"] = ent
                break

        if not result["entity"]:
            return result

        eid = result["entity"].id
        for rel in self.relationships:
            if rel.from_entity == eid:
                to_ent = self.entities.get(rel.to_entity)
                result["outgoing"].append({"relation": rel.relation.value, "to": to_ent})
                if to_ent:
                    result["related_entities"][to_ent.id] = to_ent
            if rel.to_entity == eid:
                from_ent = self.entities.get(rel.from_entity)
                result["incoming"].append({"relation": rel.relation.value, "from": from_ent})
                if from_ent:
                    result["related_entities"][from_ent.id] = from_ent

        return result

    def find_path(self, from_entity: str, to_entity: str) -> list[str]:
        """Find relationship path between two entities (BFS)."""
        from_id = None
        to_id = None
        for eid, ent in self.entities.items():
            if from_entity.lower() in ent.name.lower():
                from_id = eid
            if to_entity.lower() in ent.name.lower():
                to_id = eid
        if not from_id or not to_id:
            return []

        adj: dict[str, list[tuple[str, str]]] = {}
        for rel in self.relationships:
            if rel.from_entity not in adj:
                adj[rel.from_entity] = []
            adj[rel.from_entity].append((rel.to_entity, rel.relation.value))

        q = deque([(from_id, [from_id])])
        seen = {from_id}
        while q:
            cur, path = q.popleft()
            if cur == to_id:
                return [self.entities.get(p, Entity(p, p, EntityType.ROOM)).name for p in path]
            for nxt, _ in adj.get(cur, []):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, path + [nxt]))
        return []

    def get_entities_by_type(self, entity_type: EntityType) -> list[Entity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities.values() if e.type == entity_type]

    def to_context_string(self, query_result: dict) -> str:
        """Convert query result to readable string for LLM context."""
        lines = []
        ent = query_result.get("entity")
        if not ent:
            return "No matching entity found."

        lines.append(f"{ent.name} ({ent.type.value}):")
        for k, v in ent.properties.items():
            lines.append(f"  - {k}: {v}")
        if ent.last_updated:
            lines.append(f"  - last_updated: {ent.last_updated}")

        for r in query_result.get("outgoing", []):
            to_ent = r.get("to")
            to_name = to_ent.name if to_ent else r.get("to")
            lines.append(f"  - {r['relation']} → {to_name}")
        for r in query_result.get("incoming", []):
            from_ent = r.get("from")
            from_name = from_ent.name if from_ent else r.get("from")
            lines.append(f"  - ← {r['relation']} from {from_name}")

        return "\n".join(lines)
