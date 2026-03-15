"""
The memory module — creates and retrieves memories.

From lesson: 'a specialized memory module... What the memory module
does depends on the nature of the memory data'

Two responsibilities: STORE and RETRIEVE.
"""

from datetime import datetime

from .vector_db import VectorDatabase, VectorRecord
from .episodic_store import EpisodicStore
from .procedural_store import ProceduralStore


class MemoryModule:
    def __init__(
        self,
        vector_db: VectorDatabase,
        episodic_store: EpisodicStore,
        procedural_store: ProceduralStore,
    ):
        self.db = vector_db
        self.episodic = episodic_store
        self.procedural = procedural_store

    def store_session(self, session_data: dict):
        """After task completion: store both memory types."""
        print("[MEMORY MODULE] Storing session memories...")

        ep_record = self.episodic.create_record(session_data)
        prefs = ep_record.user_preferences
        if prefs:
            print("[MEMORY MODULE] Episodic: User preferences captured")
            for k, v in prefs.items():
                print(f"                    → {k}: {v}")

        proc_data = {
            **session_data,
            "task_type": "meeting",
            "template_id": f"PR-{datetime.now().strftime('%H%M%S')}",
        }
        skill = self.procedural.create_skill_template(proc_data)
        print("[MEMORY MODULE] Procedural: Skill template created")
        print(f"                    → Optimal sequence: {'→'.join(skill.optimal_tool_sequence)}")
        if skill.notes:
            print(f"                    → {skill.notes}")

        self.db.store(
            VectorRecord(
                record_id=ep_record.record_id,
                record_type="episodic",
                content={
                    "user": ep_record.user_id,
                    "preferences": prefs,
                    "feedback": ep_record.feedback,
                },
                vector=[],
                timestamp=ep_record.timestamp,
            )
        )
        self.db.store(
            VectorRecord(
                record_id=skill.template_id,
                record_type="procedural",
                content={
                    "sequence": skill.optimal_tool_sequence,
                    "latencies": skill.tool_latencies,
                    "notes": skill.notes,
                },
                vector=[],
                timestamp=skill.timestamp,
            )
        )

    def retrieve_context(self, current_task: str, user_id: str) -> dict:
        """For new task: retrieve relevant memories."""
        print("[MEMORY MODULE] Retrieving context for task...")

        ep_results = self.db.query(current_task, record_type="episodic", top_k=3)
        proc_results = self.db.query(current_task, record_type="procedural", top_k=2)

        episodic_context = []
        for r in ep_results:
            prefs = r.content.get("preferences", {})
            for k, v in prefs.items():
                episodic_context.append(f"→ {user_id} prefers {k}: {v}")

        procedural_context = []
        for r in proc_results:
            seq = r.content.get("sequence", [])
            notes = r.content.get("notes", "")
            procedural_context.append(f"→ Optimal sequence: {'→'.join(seq)}")
            if notes:
                procedural_context.append(f"→ {notes}")

        if episodic_context:
            print("[VECTOR DB] Found relevant preferences:")
            for line in episodic_context[:3]:
                print(f"                {line}")
        if procedural_context:
            print("[VECTOR DB] Found relevant skill template:")
            for line in procedural_context[:3]:
                print(f"                {line}")

        print("[MEMORY MODULE] Context ready for LLM injection ✓")

        return {
            "episodic": "\n".join(episodic_context) or "No episodic memories found",
            "procedural": "\n".join(procedural_context) or "No procedural memories found",
        }
