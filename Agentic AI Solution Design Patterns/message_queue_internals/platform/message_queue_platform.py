"""
Message Queue Platform — Orchestrates all 6 internal components.
"""

import uuid
from datetime import datetime

from .components import (
    Message,
    MessageType,
    RequestQueue,
    MessageStore,
    RequestDispatcher,
    ResponseQueue,
    ResponseDispatcher,
    AckHandler,
)


class MessageQueuePlatform:
    """
    Orchestrates ALL internal components.

    From lesson: 'In a messaging queue platform, there are
    several moving parts that manage and control the flow
    of messages to ensure reliable and asynchronous
    communication between agents or services.'

    This is the unified platform that agents interact with.
    Internally coordinates all 6 components.
    """

    def __init__(self, platform_name: str):
        self.name = platform_name

        self.request_store = MessageStore("request_store")
        self.response_store = MessageStore("response_store")
        self.request_queue = RequestQueue()
        self.response_queue = ResponseQueue()
        self.request_dispatcher = RequestDispatcher()
        self.response_dispatcher = ResponseDispatcher()
        self.ack_handler = AckHandler(self.request_store)

        self._processed_request_count = 0
        self._processed_response_count = 0

    def producer_send_request(
        self,
        sender_id: str,
        recipient_id: str,
        payload: dict,
        expects_response: bool = True,
    ) -> str:
        """
        Producer sends request message.

        Flow:
        1. Create message with unique IDs
        2. Add to request_queue
        3. Persist in request_store
        4. If expects_response: register in response_dispatcher
        5. Return correlation_id for tracking
        """
        msg_id = str(uuid.uuid4())[:8]
        corr_id = str(uuid.uuid4())[:8]
        message = Message(
            message_id=msg_id,
            correlation_id=corr_id,
            message_type=MessageType.REQUEST,
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload=payload,
            timestamp=datetime.now().strftime("%H:%M:%S"),
        )
        self.request_queue.enqueue(message)
        self.request_store.persist(message)
        if expects_response:
            self.response_dispatcher.register_producer_waiting(sender_id, corr_id)
        print(f"📤 Producer continues without waiting ✓")
        return corr_id

    def consumer_connect_and_receive(
        self,
        consumer_id: str,
    ) -> Message | None:
        """
        Consumer connects and polls for message.

        Flow:
        1. consumer_connects() in request_dispatcher
        2. dispatcher.dispatch() sends message
        3. Returns message to consumer
        """
        print(f"📥 Consumer connecting and polling...")
        self.request_dispatcher.consumer_connects(consumer_id)
        msg, _ = self.request_dispatcher.dispatch(self.request_queue)
        return msg

    def consumer_acknowledge(
        self,
        consumer_id: str,
        message: Message,
    ):
        """Consumer acknowledges receipt. Routes to ack_handler."""
        self.ack_handler.receive_ack(message.message_id, consumer_id)

    def consumer_send_response(
        self,
        consumer_id: str,
        original_message: Message,
        response_payload: dict,
    ):
        """
        Consumer becomes producer for response.

        Flow:
        1. Create response with SAME correlation_id
        2. Add to response_queue
        3. Persist in response_store
        """
        # Role reversal - consumer becomes producer
        resp_id = str(uuid.uuid4())[:8]
        response = Message(
            message_id=resp_id,
            correlation_id=original_message.correlation_id,
            message_type=MessageType.RESPONSE,
            sender_id=consumer_id,
            recipient_id=original_message.sender_id,
            payload=response_payload,
            timestamp=datetime.now().strftime("%H:%M:%S"),
        )
        self.response_queue.enqueue_response(response)
        self.response_store.persist(response)

    def producer_receive_response(
        self,
        producer_id: str,
        correlation_id: str,
    ) -> Message | None:
        """
        Original producer receives correlated response.

        Flow:
        1. response_dispatcher.dispatch_response()
        2. Match by correlation_id
        3. Return to original producer
        """
        response, _ = self.response_dispatcher.dispatch_response(
            self.response_queue, correlation_id
        )
        if response and response.message_id in self.response_store._store:
            self.response_store.remove(response.message_id)
        return response

    def simulate_platform_failure_and_recovery(self):
        """
        Demonstrate fault tolerance.
        Both stores simulate failure and recovery.
        Re-queue recovered requests for processing.
        """
        # Simulate crash: clear in-memory queue (persistent store survives)
        self.request_queue._queue.clear()
        recovered_req = self.request_store.simulate_failure_and_recovery()
        for msg in recovered_req:
            if not msg.acknowledged:
                self.request_queue._queue.append(msg)
        print(f"                   Processing continues from recovery point")

    def get_platform_status(self) -> dict:
        """Current status of all components."""
        return {
            "request_queue_depth": self.request_queue.size(),
            "response_queue_depth": self.response_queue.size(),
            "request_store_count": self.request_store.get_count(),
            "response_store_count": self.response_store.get_count(),
            "connected_consumers": [
                c for c, r in self.request_dispatcher._connected_consumers.items() if r
            ],
            "acks_processed": self.ack_handler.get_ack_count(),
            "dispatched_requests": len(self.request_dispatcher._dispatch_log),
        }
