"""
Route Optimization Agent — AGENT 2: Calculates optimal routes.
"""

from message_queue import CentralMessageQueue, LogisticsMessage, MessageCategory
from data.traffic import TRAFFIC_CONDITIONS
from prompts import ROUTE_OPTIMIZATION_PROMPT


class RouteOptimizationAgent:
    """
    AGENT 2: Route Optimization Agent

    From lesson: 'a route optimization agent, acting as
    the consumer, polls the message queue when it's ready
    and has available processing power. It then calculates
    the most efficient delivery route, considering factors
    like traffic, delivery time window, and vehicle capacity.'
    """

    agent_id = "route_optimization_agent"

    def __init__(self, llm_client, queue: CentralMessageQueue):
        self.llm = llm_client
        self.queue = queue

    def poll_and_optimize(self) -> LogisticsMessage | None:
        """
        CONSUMER → PRODUCER:
        1. Poll queue for NEW_ORDER messages
        2. LLM calculates optimal route
        3. Send OPTIMIZED_ROUTE message
        4. Keep same correlation_id
        """
        msg = self.queue.poll(self.agent_id, MessageCategory.NEW_ORDER)
        if not msg:
            return None
        order = msg.payload.get("order", {})
        try:
            content = self.llm.generate(
                "You are a route optimization agent.",
                ROUTE_OPTIMIZATION_PROMPT.format(
                    order=order,
                    traffic=TRAFFIC_CONDITIONS,
                    pickup=order.get("pickup", ""),
                    delivery=order.get("delivery", ""),
                    time_window=order.get("time_window", ""),
                    weight_kg=order.get("weight_kg", 0),
                ),
            )
        except Exception:
            content = "RECOMMENDED_ROUTE: Via Highway B2. ESTIMATED_DURATION: 45min. DISTANCE_KM: 12"
        print(f"💭 LLM: Calculating route for {order.get('customer', '')}...")
        print(f"   Traffic: {TRAFFIC_CONDITIONS.get(order.get('delivery', '').split()[0], 'moderate')}")
        print(f"   Time window: {order.get('time_window', '')}")
        print(f"   Route: {content[:80]}...")
        route_msg = LogisticsMessage(
            correlation_id=msg.correlation_id,
            category=MessageCategory.OPTIMIZED_ROUTE,
            sender_id=self.agent_id,
            payload={
                "order": order,
                "route": content,
                "correlation_id": msg.correlation_id,
            },
        )
        route_msg.priority = msg.priority
        self.queue.send(route_msg)
        print(f"   (route_optimization_agent now acting as PRODUCER)")
        return route_msg
