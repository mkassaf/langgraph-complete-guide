"""
Graph Builder — Builds and maintains the office knowledge graph.

Maintained by human experts (AI engineers + domain specialists).
"""

from graph.knowledge_graph import (
    KnowledgeGraph,
    Entity,
    EntityType,
    Relationship,
    RelationType,
)


class GraphBuilder:
    """
    Builds and maintains the office knowledge graph.
    """

    def build_office_graph(self) -> KnowledgeGraph:
        """Build complete office building knowledge graph."""
        g = KnowledgeGraph()

        # ROOMS
        g.add_entity(Entity("room_301", "Room 301", EntityType.ROOM, {"floor": 3, "capacity": 10, "type": "meeting"}))
        g.add_entity(Entity("room_303", "Room 303", EntityType.ROOM, {"floor": 3, "capacity": 20, "type": "IT"}))
        g.add_entity(Entity("room_205", "Room 205", EntityType.ROOM, {"floor": 2, "capacity": 15, "type": "HR"}))
        g.add_entity(Entity("supply_a", "Supply Room A", EntityType.ROOM, {"floor": 1}))

        # EQUIPMENT (printer initially in 301, will be moved in simulate_recent_change)
        g.add_entity(Entity("printer", "Printer HP-LaserJet", EntityType.EQUIPMENT, {
            "status": "operational", "last_maintained": "January 2026"
        }, last_updated="March 2026"))
        g.add_entity(Entity("projector", "Projector Sony-4K", EntityType.EQUIPMENT, {"status": "operational"}))
        g.add_entity(Entity("coffee", "Coffee Machine", EntityType.EQUIPMENT, {"status": "needs_maintenance"}))

        # PEOPLE
        g.add_entity(Entity("alice", "Alice", EntityType.PERSON, {"role": "IT Manager"}))
        g.add_entity(Entity("bob", "Bob", EntityType.PERSON, {"role": "HR Director"}))
        g.add_entity(Entity("carol", "Carol", EntityType.PERSON, {"role": "Facilities"}))

        # SUPPLIES
        g.add_entity(Entity("paper", "A4 Paper", EntityType.SUPPLY))
        g.add_entity(Entity("beans", "Coffee Beans", EntityType.SUPPLY))

        # DEPARTMENTS
        g.add_entity(Entity("it_dept", "IT Department", EntityType.DEPARTMENT))
        g.add_entity(Entity("hr_dept", "HR Department", EntityType.DEPARTMENT))

        # RELATIONSHIPS (printer in 301 initially)
        g.add_relationship(Relationship("printer", RelationType.LOCATED_IN, "room_301"))
        g.add_relationship(Relationship("printer", RelationType.USES, "paper"))
        g.add_relationship(Relationship("alice", RelationType.WORKS_IN, "room_303"))
        g.add_relationship(Relationship("alice", RelationType.MANAGES, "it_dept"))
        g.add_relationship(Relationship("bob", RelationType.WORKS_IN, "room_205"))
        g.add_relationship(Relationship("bob", RelationType.MANAGES, "hr_dept"))
        g.add_relationship(Relationship("room_303", RelationType.CONNECTED_TO, "supply_a"))
        g.add_relationship(Relationship("room_301", RelationType.CONNECTED_TO, "room_303"))
        g.add_relationship(Relationship("carol", RelationType.MANAGES, "printer"))
        g.add_relationship(Relationship("carol", RelationType.MANAGES, "projector"))
        g.add_relationship(Relationship("projector", RelationType.LOCATED_IN, "room_301"))
        g.add_relationship(Relationship("coffee", RelationType.LOCATED_IN, "room_205"))
        g.add_relationship(Relationship("paper", RelationType.AVAILABLE_IN, "room_303"))
        g.add_relationship(Relationship("paper", RelationType.LOCATED_IN, "supply_a"))
        g.add_relationship(Relationship("beans", RelationType.LOCATED_IN, "room_205"))
        g.add_relationship(Relationship("it_dept", RelationType.LOCATED_IN, "room_303"))
        g.add_relationship(Relationship("hr_dept", RelationType.LOCATED_IN, "room_205"))

        return g

    def simulate_recent_change(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        """
        Simulate a recent change NOT in LLM training data:
        Move printer from Room 301 to Room 303.
        """
        # Remove old LOCATED_IN
        graph.relationships = [
            r for r in graph.relationships
            if not (r.from_entity == "printer" and r.relation == RelationType.LOCATED_IN)
        ]
        graph.add_relationship(Relationship("printer", RelationType.LOCATED_IN, "room_303"))
        if "printer" in graph.entities:
            e = graph.entities["printer"]
            graph.entities["printer"] = Entity(
                e.id, e.name, e.type,
                {**e.properties, "previous_location": "Room 301"},
                last_updated="March 2026"
            )
        return graph
