"""
Shipping Agent — arranges final shipment.
"""

from memory.memory_types import StateCategory
from memory.shared_memory import SharedMemorySystem
from memory.agent_memory import AgentMemory
from prompts import AGENT_DECISION_PROMPT, NO_SHARED_MEMORY_CONTEXT, SHARED_MEMORY_CONTEXT


class ShippingAgent:
    """
    Arranges final shipment.
    Reads packed status from shared memory when available.
    """

    agent_id = "shipping_agent"

    def __init__(self, llm_client, private_memory: AgentMemory, shared_memory: SharedMemorySystem | None):
        self.llm = llm_client
        self.private_memory = private_memory
        self.shared_memory = shared_memory

    def arrange_shipment(self, order: dict, order_id: str = "ORD-2847") -> dict:
        """Arrange shipment. Uses shared memory for current order status."""
        self.private_memory.update_objective("Arrange shipment")

        if self.shared_memory:
            shared_ctx = self._get_shared_context()
            prompt = AGENT_DECISION_PROMPT.format(
                agent_type="shipping",
                private_memory=self.private_memory.get_context_summary(),
                shared_memory_context=SHARED_MEMORY_CONTEXT.format(shared_state=shared_ctx),
                task="Read packing status from shared memory. Arrange shipment. Write tracking to shared memory.",
            )
        else:
            prompt = AGENT_DECISION_PROMPT.format(
                agent_type="shipping",
                private_memory=self.private_memory.get_context_summary(),
                shared_memory_context=NO_SHARED_MEMORY_CONTEXT,
                task="Use original order details (stale - no shared memory). Arrange shipment.",
            )

        try:
            content = self.llm.generate("You are a shipping agent.", prompt)
            return self._process_response(content, order_id)
        except Exception:
            return self._fallback_ship(order_id)

    def _get_shared_context(self) -> str:
        if not self.shared_memory:
            return "None"
        entries = list(self.shared_memory.store.values())
        return "\n".join(f"  {e.key}: {e.value}" for e in entries[:20]) or "Empty"

    def _process_response(self, content: str, order_id: str) -> dict:
        result = {"success": True, "carrier": "FastShip", "tracking": "FS-8847291", "writes": []}
        if self.shared_memory:
            self.shared_memory.write(
                f"shipping/{order_id}",
                {"status": "dispatched", "carrier": result["carrier"], "tracking": result["tracking"]},
                StateCategory.ORDER_STATUS,
                self.agent_id,
            )
            result["writes"].append((f"shipping/{order_id}", "dispatched"))
        self.private_memory.record_action("ship", result["tracking"])
        return result

    def _fallback_ship(self, order_id: str) -> dict:
        result = {"success": True, "carrier": "FastShip", "tracking": "FS-8847291", "writes": []}
        if self.shared_memory:
            self.shared_memory.write(
                f"shipping/{order_id}",
                {"status": "dispatched", "carrier": result["carrier"], "tracking": result["tracking"]},
                StateCategory.ORDER_STATUS,
                self.agent_id,
            )
            result["writes"].append((f"shipping/{order_id}", "dispatched"))
        return result
