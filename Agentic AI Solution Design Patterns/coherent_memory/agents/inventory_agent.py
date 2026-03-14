"""
Inventory Agent — tracks and manages stock levels.
"""

import re
from memory.memory_types import StateCategory
from memory.shared_memory import SharedMemorySystem
from memory.agent_memory import AgentMemory
from prompts import AGENT_DECISION_PROMPT, NO_SHARED_MEMORY_CONTEXT, SHARED_MEMORY_CONTEXT


class InventoryAgent:
    """
    Tracks and manages stock levels.
    Writes reservations to shared memory when available.
    """

    agent_id = "inventory_agent"
    STOCK = {
        "BW-001": {"name": "Blue Widget", "quantity": 5, "location": "A-12"},
        "RG-042": {"name": "Red Gadget", "quantity": 2, "location": "B-07"},
        "GT-103": {"name": "Green Tool", "quantity": 8, "location": "C-03"},
    }

    def __init__(self, llm_client, private_memory: AgentMemory, shared_memory: SharedMemorySystem | None):
        self.llm = llm_client
        self.private_memory = private_memory
        self.shared_memory = shared_memory

    def check_and_reserve_items(self, order: dict) -> dict:
        """Check if order can be fulfilled. Reserve items in shared memory if yes."""
        self.private_memory.update_objective("Reserve items for order")
        items = order.get("items", [])
        stock = dict(self.STOCK)

        if self.shared_memory:
            shared_ctx = self._get_shared_context()
            prompt = AGENT_DECISION_PROMPT.format(
                agent_type="inventory",
                private_memory=self.private_memory.get_context_summary(),
                shared_memory_context=SHARED_MEMORY_CONTEXT.format(shared_state=shared_ctx),
                task=f"Order needs: {items}. Current stock: {stock}. Reserve items and write to shared memory.",
            )
        else:
            prompt = AGENT_DECISION_PROMPT.format(
                agent_type="inventory",
                private_memory=self.private_memory.get_context_summary(),
                shared_memory_context=NO_SHARED_MEMORY_CONTEXT,
                task=f"Order needs: {items}. Current stock: {stock}. Reserve items (private memory only).",
            )

        try:
            content = self.llm.generate("You are an inventory agent.", prompt)
            return self._process_response(content, order)
        except Exception:
            return self._fallback_reserve(order)

    def _get_shared_context(self) -> str:
        if not self.shared_memory:
            return "None"
        entries = list(self.shared_memory.store.values())
        return "\n".join(f"  {e.key}: {e.value}" for e in entries[:20]) or "Empty"

    def _process_response(self, content: str, order: dict) -> dict:
        result = {"success": True, "reserved": {}, "writes": []}

        if self.shared_memory:
            for sku in ["BW-001", "RG-042", "GT-103"]:
                if sku in str(order.get("items", [])) or sku in content:
                    qty = 3 if sku == "BW-001" else 1 if sku == "RG-042" else 2
                    entry = self.shared_memory.write(
                        f"inventory/{sku}",
                        {"qty": self.STOCK[sku]["quantity"], "reserved": qty, "available": self.STOCK[sku]["quantity"] - qty},
                        StateCategory.INVENTORY,
                        self.agent_id,
                    )
                    result["reserved"][sku] = qty
                    result["writes"].append((f"inventory/{sku}", entry.value))

            self.shared_memory.write(
                "order/ORD-2847/status",
                "items_reserved",
                StateCategory.ORDER_STATUS,
                self.agent_id,
            )
            result["writes"].append(("order/ORD-2847/status", "items_reserved"))

        self.private_memory.record_action("reserve", str(result["reserved"]))
        return result

    def _fallback_reserve(self, order: dict) -> dict:
        result = {"success": True, "reserved": {"BW-001": 3, "RG-042": 1, "GT-103": 2}, "writes": []}
        if self.shared_memory:
            for sku, qty in result["reserved"].items():
                self.shared_memory.write(
                    f"inventory/{sku}",
                    {"qty": self.STOCK[sku]["quantity"], "reserved": qty, "available": self.STOCK[sku]["quantity"] - qty},
                    StateCategory.INVENTORY,
                    self.agent_id,
                )
                result["writes"].append((f"inventory/{sku}", {"reserved": qty}))
            self.shared_memory.write("order/ORD-2847/status", "items_reserved", StateCategory.ORDER_STATUS, self.agent_id)
            result["writes"].append(("order/ORD-2847/status", "items_reserved"))
        return result

    def update_stock_in_shared_memory(self, sku: str, new_qty: int):
        """Write stock update to shared memory."""
        if self.shared_memory:
            self.shared_memory.write(
                f"inventory/{sku}",
                {"qty": new_qty, "reserved": 0, "available": new_qty},
                StateCategory.INVENTORY,
                self.agent_id,
            )
