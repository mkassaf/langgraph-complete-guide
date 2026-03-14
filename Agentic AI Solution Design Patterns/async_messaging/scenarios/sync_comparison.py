"""
Sync Comparison Scenario — Shows problems with synchronous messaging.
"""

import time

from llm_client import LLMClient
from agents.order_agent import OrderAgent


class SyncComparisonScenario:
    """
    Shows the PROBLEMS with synchronous messaging
    to motivate why async is needed.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def run(self) -> dict:
        """
        Process 5 orders synchronously.
        Show:
        - Agent A blocked waiting for Agent B
        - Agent B blocked waiting for Agent C
        - Total time = sum of all wait times
        - If one agent fails, entire chain breaks
        """
        order_agent = OrderAgent(self.llm)
        start = time.perf_counter()
        success_count = 0
        fail_at = 3  # Simulate payment_agent crash on 3rd order
        for i, order in enumerate(OrderAgent.SAMPLE_ORDERS):
            print(f"ORD-{i+1:03d}: Agent blocked for 0.4s waiting for inventory")
            time.sleep(0.4)
            if i + 1 == fail_at:
                print(f"ORD-00{i+1}: payment_agent CRASHED → entire chain FAILED ❌")
                break
            print(f"ORD-{i+1:03d}: Agent blocked for 0.3s waiting for payment")
            time.sleep(0.3)
            success_count += 1
        elapsed = time.perf_counter() - start
        total_orders = len(OrderAgent.SAMPLE_ORDERS)
        success_rate = int(100 * success_count / total_orders) if total_orders else 0
        return {
            "total_time": elapsed,
            "success_count": success_count,
            "total_orders": total_orders,
            "success_rate": success_rate,
        }
