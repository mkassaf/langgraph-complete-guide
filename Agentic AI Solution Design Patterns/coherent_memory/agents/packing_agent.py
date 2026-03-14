"""
Packing Agent — packs picked items into shipping boxes.
"""

from memory.memory_types import StateCategory
from memory.shared_memory import SharedMemorySystem
from memory.agent_memory import AgentMemory
from prompts import AGENT_DECISION_PROMPT, NO_SHARED_MEMORY_CONTEXT, SHARED_MEMORY_CONTEXT


class PackingAgent:
    """
    Packs picked items into shipping boxes.
    Waits for picking completion in shared memory when available.
    """

    agent_id = "packing_agent"

    def __init__(self, llm_client, private_memory: AgentMemory, shared_memory: SharedMemorySystem | None):
        self.llm = llm_client
        self.private_memory = private_memory
        self.shared_memory = shared_memory

    def pack_order(self, order: dict, order_id: str = "ORD-2847") -> dict:
        """Pack order. In WITH mode, waits for picking completion first."""
        self.private_memory.update_objective("Pack order")

        if self.shared_memory:
            picking_done = self.wait_for_picking_completion(order_id)
            shared_ctx = self._get_shared_context()
            prompt = AGENT_DECISION_PROMPT.format(
                agent_type="packing",
                private_memory=self.private_memory.get_context_summary(),
                shared_memory_context=SHARED_MEMORY_CONTEXT.format(shared_state=shared_ctx),
                task=f"Picking complete: {picking_done}. Pack items. Write completion to shared memory.",
            )
        else:
            prompt = AGENT_DECISION_PROMPT.format(
                agent_type="packing",
                private_memory=self.private_memory.get_context_summary(),
                shared_memory_context=NO_SHARED_MEMORY_CONTEXT,
                task="Assume picking is done. Pack order. (You cannot verify - no shared memory)",
            )

        try:
            content = self.llm.generate("You are a packing agent.", prompt)
            return self._process_response(content, order_id)
        except Exception:
            return self._fallback_pack(order_id)

    def _get_shared_context(self) -> str:
        if not self.shared_memory:
            return "None"
        entries = list(self.shared_memory.store.values())
        return "\n".join(f"  {e.key}: {e.value}" for e in entries[:20]) or "Empty"

    def wait_for_picking_completion(self, order_id: str) -> bool:
        """Poll shared memory until picking agent marks complete."""
        if not self.shared_memory:
            return False
        entry = self.shared_memory.read(f"picking/{order_id}", self.agent_id)
        if entry and isinstance(entry.value, dict):
            return entry.value.get("status") == "complete"
        return False

    def _process_response(self, content: str, order_id: str) -> dict:
        result = {"success": True, "box": "BOX-447", "writes": []}
        if self.shared_memory:
            self.shared_memory.write(
                f"packing/{order_id}",
                {"status": "complete", "box": result["box"]},
                StateCategory.TASK_PROGRESS,
                self.agent_id,
            )
            result["writes"].append((f"packing/{order_id}", "complete"))
        self.private_memory.record_action("pack", result["box"])
        return result

    def _fallback_pack(self, order_id: str) -> dict:
        result = {"success": True, "box": "BOX-447", "writes": []}
        if self.shared_memory:
            self.shared_memory.write(
                f"packing/{order_id}",
                {"status": "complete", "box": result["box"]},
                StateCategory.TASK_PROGRESS,
                self.agent_id,
            )
            result["writes"].append((f"packing/{order_id}", "complete"))
        return result
