"""
Scenario WITHOUT shared memory — demonstrates conflicts.
"""

from memory.agent_memory import AgentMemory
from agents.inventory_agent import InventoryAgent
from agents.picking_agent import PickingAgent
from agents.packing_agent import PackingAgent
from agents.shipping_agent import ShippingAgent


class WithoutSharedMemoryScenario:
    """
    Demonstrates problems when agents lack shared memory.

    Problems:
    1. Inventory reserves - picking doesn't know
    2. Picking may duplicate (doesn't know reserved)
    3. Packing starts before picking completes (race)
    4. Shipping uses outdated order info (stale)
    """

    def __init__(self, llm_client):
        self.llm = llm_client
        self.conflicts: list[str] = []
        self.duplicate_work: list[str] = []
        self.race_conditions: list[str] = []
        self.stale_data: list[str] = []

    def run(self, order: str) -> dict:
        """Run all 4 agents WITHOUT shared memory."""
        order_data = self._parse_order(order)
        inv_mem = AgentMemory("inventory_agent")
        pick_mem = AgentMemory("picking_agent")
        pack_mem = AgentMemory("packing_agent")
        ship_mem = AgentMemory("shipping_agent")

        inv = InventoryAgent(self.llm, inv_mem, None)
        pick = PickingAgent(self.llm, pick_mem, None)
        pack = PackingAgent(self.llm, pack_mem, None)
        ship = ShippingAgent(self.llm, ship_mem, None)

        results = {}

        # 1. Inventory reserves (private only - picking won't see)
        r1 = inv.check_and_reserve_items(order_data)
        results["inventory"] = r1
        self.conflicts.append("Inventory reserved items but picking agent has no way to know")

        # 2. Picking - doesn't know about reservation, may "reserve" again
        r2 = pick.pick_items(order_data.get("items", {}), "ORD-2847")
        results["picking"] = r2
        self.duplicate_work.append("Picking agent picked same items inventory reserved (no visibility)")
        self.conflicts.append("Picking and inventory both 'handled' same items - potential double allocation")

        # 3. Packing - assumes picking done (race condition)
        r3 = pack.pack_order(order_data, "ORD-2847")
        results["packing"] = r3
        self.race_conditions.append("Packing started without verifying picking complete - assumed yes")

        # 4. Shipping - uses original order (stale)
        r4 = ship.arrange_shipment(order_data, "ORD-2847")
        results["shipping"] = r4
        self.stale_data.append("Shipping used original order details - no visibility into actual packing/shipping status")

        return {
            "success": False,
            "results": results,
            "conflicts": self.conflicts,
            "duplicate_work": self.duplicate_work,
            "race_conditions": self.race_conditions,
            "stale_data": self.stale_data,
        }

    def _parse_order(self, order: str) -> dict:
        return {
            "order_id": "ORD-2847",
            "items": {"BW-001": 3, "RG-042": 1, "GT-103": 2},
            "priority": "HIGH",
            "customer": "Acme Corp",
        }
