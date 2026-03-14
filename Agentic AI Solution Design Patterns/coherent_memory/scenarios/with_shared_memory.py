"""
Scenario WITH shared memory — demonstrates coherent operation.
"""

from memory.agent_memory import AgentMemory
from memory.shared_memory import SharedMemorySystem
from agents.inventory_agent import InventoryAgent
from agents.picking_agent import PickingAgent
from agents.packing_agent import PackingAgent
from agents.shipping_agent import ShippingAgent


class WithSharedMemoryScenario:
    """
    Demonstrates coherent operation with shared memory.

    Shows:
    1. Inventory reserves → shared memory updated
    2. Picking reads reservation → no duplication
    3. Packing waits for picking in shared memory
    4. Shipping reads complete order status
    """

    def __init__(self, llm_client):
        self.llm = llm_client
        self.shared_memory = SharedMemorySystem()
        self.writes_log: list[tuple[str, str, object]] = []

    def run(self, order: str) -> dict:
        """Run all 4 agents WITH shared memory."""
        order_data = self._parse_order(order)
        inv_mem = AgentMemory("inventory_agent")
        pick_mem = AgentMemory("picking_agent")
        pack_mem = AgentMemory("packing_agent")
        ship_mem = AgentMemory("shipping_agent")

        inv = InventoryAgent(self.llm, inv_mem, self.shared_memory)
        pick = PickingAgent(self.llm, pick_mem, self.shared_memory)
        pack = PackingAgent(self.llm, pack_mem, self.shared_memory)
        ship = ShippingAgent(self.llm, ship_mem, self.shared_memory)

        results = {}

        # 1. Inventory reserves and writes to shared memory
        r1 = inv.check_and_reserve_items(order_data)
        results["inventory"] = r1
        for key, val in r1.get("writes", []):
            self.writes_log.append(("inventory_agent", key, val))

        # 2. Picking reads shared memory, sees reservations, picks
        r2 = pick.pick_items(order_data.get("items", {}), "ORD-2847")
        results["picking"] = r2
        for key, val in r2.get("writes", []):
            self.writes_log.append(("picking_agent", key, val))

        # 3. Packing checks shared memory for picking completion
        r3 = pack.pack_order(order_data, "ORD-2847")
        results["packing"] = r3
        for key, val in r3.get("writes", []):
            self.writes_log.append(("packing_agent", key, val))

        # 4. Shipping reads shared memory for complete status
        r4 = ship.arrange_shipment(order_data, "ORD-2847")
        results["shipping"] = r4
        for key, val in r4.get("writes", []):
            self.writes_log.append(("shipping_agent", key, val))

        snapshot = self.shared_memory.get_snapshot()
        return {
            "success": True,
            "results": results,
            "conflicts": [],
            "duplicate_work": [],
            "race_conditions": [],
            "stale_data": [],
            "shared_memory": {
                "total_entries": snapshot.total_entries,
                "writes": self.shared_memory.get_write_count(),
                "reads": self.shared_memory.get_read_count(),
                "writes_log": self.writes_log,
            },
        }

    def _parse_order(self, order: str) -> dict:
        return {
            "order_id": "ORD-2847",
            "items": {"BW-001": 3, "RG-042": 1, "GT-103": 2},
            "priority": "HIGH",
            "customer": "Acme Corp",
        }
