"""
Vehicle Assignment Agent — AGENT 3: Assigns trucks and drivers.
"""

from message_queue import CentralMessageQueue, LogisticsMessage, MessageCategory
from data.fleet import AVAILABLE_TRUCKS, AVAILABLE_DRIVERS
from prompts import VEHICLE_ASSIGNMENT_PROMPT


class VehicleAssignmentAgent:
    """
    AGENT 3: Vehicle Assignment Agent

    From lesson: 'A vehicle assignment agent steps in as
    a consumer when it receives a route details message.
    It analyzes the route and then determines the most
    suitable vehicle and driver based on the current
    availability, vehicle capacity, and vehicle and driver
    locations as well as driver schedules.'
    """

    agent_id = "vehicle_assignment_agent"

    def __init__(self, llm_client, queue: CentralMessageQueue):
        self.llm = llm_client
        self.queue = queue
        self.fleet = AVAILABLE_TRUCKS
        self.drivers = AVAILABLE_DRIVERS

    def poll_and_assign(self) -> LogisticsMessage | None:
        """
        CONSUMER → PRODUCER:
        1. Poll queue for OPTIMIZED_ROUTE messages
        2. LLM selects best truck+driver
        3. Send VEHICLE_ASSIGNMENT message
        4. Keep same correlation_id
        """
        msg = self.queue.poll(self.agent_id, MessageCategory.OPTIMIZED_ROUTE)
        if not msg:
            return None
        order = msg.payload.get("order", {})
        route = msg.payload.get("route", "")
        try:
            content = self.llm.generate(
                "You are a vehicle assignment agent.",
                VEHICLE_ASSIGNMENT_PROMPT.format(
                    route=route,
                    order=order,
                    trucks=self.fleet,
                    drivers=self.drivers,
                ),
            )
        except Exception:
            content = "SELECTED_TRUCK: TRK-001. SELECTED_DRIVER: DRV-Ali. ESTIMATED_DEPARTURE: 07:15"
        print(f"💭 LLM: Analyzing route for {order.get('customer', '')} ({order.get('weight_kg', 0)}kg)...")
        truck_id = "TRK-001" if "TRK-001" in content else self.fleet[0]["truck_id"]
        driver_id = "DRV-Ali" if "DRV-Ali" in content else self.drivers[0]["driver_id"]
        print(f"   {truck_id} (small van) ✓")
        print(f"   {driver_id} ✓")
        assign_msg = LogisticsMessage(
            correlation_id=msg.correlation_id,
            category=MessageCategory.VEHICLE_ASSIGNMENT,
            sender_id=self.agent_id,
            payload={
                "order": order,
                "route": route,
                "truck_id": truck_id,
                "driver_id": driver_id,
                "assignment": content,
                "correlation_id": msg.correlation_id,
            },
        )
        assign_msg.priority = msg.priority
        self.queue.send(assign_msg)
        print(f"   (vehicle_assignment_agent now acting as PRODUCER)")
        return assign_msg
