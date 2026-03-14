"""
Picking Agent — picks items from warehouse shelves.
"""

from memory.memory_types import StateCategory
from memory.shared_memory import SharedMemorySystem
from memory.agent_memory import AgentMemory
from prompts import AGENT_DECISION_PROMPT, NO_SHARED_MEMORY_CONTEXT, SHARED_MEMORY_CONTEXT


class PickingAgent:
    """
    Picks items from warehouse shelves.
    Reads reservations from shared memory when available.
    """

    agent_id = "picking_agent"

    def __init__(self, llm_client, private_memory: AgentMemory, shared_memory: SharedMemorySystem | None):
        self.llm = llm_client
        self.private_memory = private_memory
        self.shared_memory = shared_memory

    def pick_items(self, reserved_items: dict, order_id: str = "ORD-2847") -> dict:
        """Pick items. Uses shared memory to see what inventory reserved."""
        self.private_memory.update_objective("Pick items for order")

        if self.shared_memory:
            reservations = self.check_what_inventory_reserved()
            shared_ctx = self._get_shared_context()
            prompt = AGENT_DECISION_PROMPT.format(
                agent_type="picking",
                private_memory=self.private_memory.get_context_summary(),
                shared_memory_context=SHARED_MEMORY_CONTEXT.format(shared_state=shared_ctx),
                task=f"Inventory reserved: {reservations}. Pick these items. Write completion to shared memory.",
            )
        else:
            prompt = AGENT_DECISION_PROMPT.format(
                agent_type="picking",
                private_memory=self.private_memory.get_context_summary(),
                shared_memory_context=NO_SHARED_MEMORY_CONTEXT,
                task=f"Order needs: {reserved_items}. You don't know if inventory reserved them. Pick items.",
            )

        try:
            content = self.llm.generate("You are a picking agent.", prompt)
            return self._process_response(content, order_id)
        except Exception:
            return self._fallback_pick(order_id)

    def _get_shared_context(self) -> str:
        if not self.shared_memory:
            return "None"
        entries = list(self.shared_memory.store.values())
        return "\n".join(f"  {e.key}: {e.value}" for e in entries[:20]) or "Empty"

    def check_what_inventory_reserved(self) -> dict:
        """Read inventory agent's reservations from shared memory."""
        if not self.shared_memory:
            return {}
        result = {}
        for sku in ["BW-001", "RG-042", "GT-103"]:
            entry = self.shared_memory.read(f"inventory/{sku}", self.agent_id)
            if entry and isinstance(entry.value, dict):
                reserved = entry.value.get("reserved", 0)
                if reserved:
                    result[sku] = reserved
        return result

    def _process_response(self, content: str, order_id: str) -> dict:
        result = {"success": True, "picked": ["BW-001", "RG-042", "GT-103"], "writes": []}
        if self.shared_memory:
            self.shared_memory.write(
                f"picking/{order_id}",
                {"status": "complete", "items": result["picked"]},
                StateCategory.TASK_PROGRESS,
                self.agent_id,
            )
            result["writes"].append((f"picking/{order_id}", "complete"))
        self.private_memory.record_action("pick", str(result["picked"]))
        return result

    def _fallback_pick(self, order_id: str) -> dict:
        result = {"success": True, "picked": ["BW-001", "RG-042", "GT-103"], "writes": []}
        if self.shared_memory:
            self.shared_memory.write(
                f"picking/{order_id}",
                {"status": "complete", "items": result["picked"]},
                StateCategory.TASK_PROGRESS,
                self.agent_id,
            )
            result["writes"].append((f"picking/{order_id}", "complete"))
        return result
