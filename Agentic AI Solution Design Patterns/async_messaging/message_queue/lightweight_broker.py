"""
Lightweight in-memory broker for intra-agent communication.
"""

import queue

from message_queue.message import Message


class LightweightBroker:
    """
    Lightweight in-memory message broker for INTRA-agent use.

    For intra-agent communication, there are lightweight
    message brokers and in-memory queues that are often
    more suitable.

    Much simpler than MessageQueuePlatform.
    No persistence. No complex routing. Just fast in-memory.
    """

    def __init__(self):
        self._internal_queue = queue.Queue()
        self.message_count = 0

    def send_internal(self, message: Message):
        """Fast non-persistent internal send."""
        self._internal_queue.put(message)
        self.message_count += 1

    def receive_internal(self) -> Message | None:
        """Fast non-blocking internal receive."""
        try:
            return self._internal_queue.get_nowait()
        except queue.Empty:
            return None
