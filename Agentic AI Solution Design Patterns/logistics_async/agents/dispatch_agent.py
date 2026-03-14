"""
Dispatch Agent — AGENT 4: Dispatches to truck + driver.
"""

import uuid

from message_queue import CentralMessageQueue, LogisticsMessage, MessageCategory
from data.fleet import AVAILABLE_TRUCKS, AVAILABLE_DRIVERS
from prompts import DISPATCH_PROMPT


class DispatchAgent:
    """
    AGENT 4: Dispatch Agent

    From lesson: 'while the dispatch agent is listening
    for assignment confirmation messages on the message
    queue, it actually is sent this next assignment. It
    then takes all the information and sends the route
    directions and any other instructions directly to the
    assigned truck's onboard system, and also notifies
    the driver via mobile text.'
    """

    agent_id = "dispatch_agent"

    def __init__(self, llm_client, queue: CentralMessageQueue):
        self.llm = llm_client
        self.queue = queue

    def poll_and_dispatch(self) -> LogisticsMessage | None:
        """
        CONSUMER → PRODUCER:
        1. Poll queue for VEHICLE_ASSIGNMENT messages
        2. LLM prepares dispatch instructions
        3. Simulate sending to truck onboard system
        4. Simulate SMS to driver
        5. Send FULFILLMENT_CONFIRMATION
        6. Use SAME correlation_id as original order
        """
        msg = self.queue.poll(self.agent_id, MessageCategory.VEHICLE_ASSIGNMENT)
        if not msg:
            return None
        order = msg.payload.get("order", {})
        assignment = msg.payload.get("assignment", "")
        route = msg.payload.get("route", "")
        truck_id = msg.payload.get("truck_id", "TRK-001")
        driver_id = msg.payload.get("driver_id", "DRV-Ali")
        drivers = {d["driver_id"]: d for d in AVAILABLE_DRIVERS}
        driver = drivers.get(driver_id, {"name": "Driver"})
        try:
            content = self.llm.generate(
                "You are a dispatch agent.",
                DISPATCH_PROMPT.format(
                    assignment=assignment,
                    route=route,
                    order=order,
                ),
            )
        except Exception:
            content = "DISPATCH_STATUS: dispatched. TRACKING_NUMBER: TRK-882931"
        print(f"💭 LLM: Preparing dispatch for {truck_id}/{driver_id}...")
        print(f"   Generating GPS route...")
        print(f"   Preparing driver SMS...")
        self._send_to_truck_system(truck_id, {"route": route, "order": order})
        sms = f"Dispatch: {order.get('pickup', '')}→{order.get('delivery', '')}. Pickup 07:15."
        self._send_sms_to_driver(driver, sms)
        tracking = f"TRK-{str(uuid.uuid4())[:6].upper()}"
        eta = "08:45" if order.get("priority") == "critical" else "11:30"
        fulfill_msg = LogisticsMessage(
            correlation_id=msg.correlation_id,
            category=MessageCategory.FULFILLMENT_CONFIRMATION,
            sender_id=self.agent_id,
            payload={
                "order": order,
                "truck_id": truck_id,
                "driver_id": driver_id,
                "tracking": tracking,
                "eta": eta,
                "status": "DISPATCHED",
                "correlation_id": msg.correlation_id,
            },
        )
        self.queue.send(fulfill_msg)
        print(f"   (dispatch_agent now acting as PRODUCER)")
        print(f"   Correlation: {msg.correlation_id} ← SAME AS ORIGINAL!")
        return fulfill_msg

    def _send_to_truck_system(self, truck_id: str, instructions: dict):
        """Simulate sending to truck onboard computer."""
        print(f"🚛 [TRUCK SYSTEM] {truck_id} received route data")

    def _send_sms_to_driver(self, driver: dict, message: str):
        """Simulate SMS notification."""
        print(f"📱 [SMS] → {driver.get('name', 'Driver')}: {message[:60]}...")
