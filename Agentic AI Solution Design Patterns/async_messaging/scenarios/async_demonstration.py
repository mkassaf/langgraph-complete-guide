"""
Async Demonstration Scenario — All async messaging patterns.
"""

import time

from message_queue.queue_platform import MessageQueuePlatform
from llm_client import LLMClient
from agents.order_agent import OrderAgent
from agents.inventory_agent import InventoryAgent
from agents.payment_agent import PaymentAgent
from agents.fulfillment_agent import FulfillmentAgent


class AsyncDemonstrationScenario:
    """
    Shows all async messaging patterns from the lesson.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def run(self, platform: MessageQueuePlatform) -> dict:
        """
        1. Producer sends 5 orders rapidly (decoupled)
        2. Queue buffers them (load leveling)
        3. Consumers process at own pace
        4. Correlation IDs track request-responses
        5. FIFO ensures correct sequence
        6. Simulate failure → show persistence
        """
        order_agent = OrderAgent(self.llm)
        inventory_agent = InventoryAgent(self.llm)
        payment_agent = PaymentAgent(self.llm)
        fulfillment_agent = FulfillmentAgent(self.llm)

        start = time.perf_counter()

        # 1. Producer sends 5 orders rapidly
        order_agent.process_orders_async(platform)

        # 2. Inventory processes at own pace
        inventory_agent.start_processing(platform, max_messages=5)

        # 3. Payment processes with correlation IDs
        payment_agent.process_payments(platform, max_messages=5)

        # 4. Fulfillment - simulate failure mid-way
        platform.create_queue("fulfillment")
        # Messages already in fulfillment from payment_agent
        depth_before = platform.get_queue_depth("fulfillment")
        if depth_before > 0:
            platform.simulate_failure_and_recovery("fulfillment")

        # 5. Fulfillment processes in FIFO order
        fulfillment_agent.fulfill_in_order(platform, max_messages=10)

        elapsed = time.perf_counter() - start
        stats = platform.get_stats()
        return {
            "total_time": elapsed,
            "stats": stats,
            "success_count": 5,
        }
