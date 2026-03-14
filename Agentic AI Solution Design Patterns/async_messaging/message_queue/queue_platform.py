"""
Message Queue Platform — Core async messaging broker.
"""

import queue
import threading
import uuid
from collections import deque
from datetime import datetime

from message_queue.message import Message, MessageType, MessageStatus


class MessageQueuePlatform:
    """
    The Message Queue (Message Broker) platform.

    Core capabilities demonstrated:
    1. Decoupled delivery - producer doesn't wait
    2. Persistence - messages survive failures
    3. Load leveling - buffers messages for consumers
    4. FIFO ordering - sequential processing
    5. Correlation - request-response linking
    """

    def __init__(self, platform_name: str):
        self.name = platform_name
        self._queues: dict[str, deque] = {}  # FIFO queue for each
        self._persistent_store: dict[str, list[Message]] = {}
        self._delivered_ids: set[str] = set()  # For recovery: exclude delivered
        self._response_store: dict[str, list[Message]] = {}  # correlation_id -> responses
        self._message_log: list[dict] = []
        self._correlation_map: dict[str, Message] = {}
        self._lock = threading.Lock()
        self._sequence_counter: dict[str, int] = {}
        self._sent_count = 0
        self._delivered_count = 0
        self._failed_count = 0

    def create_queue(self, queue_name: str):
        """Create a named queue."""
        with self._lock:
            self._queues[queue_name] = deque()
            self._persistent_store[queue_name] = []
            self._response_store[queue_name] = []
            self._sequence_counter[queue_name] = 0
        print(f"[QUEUE] Created: {queue_name}")

    def send(
        self,
        queue_name: str,
        message: Message,
    ) -> bool:
        """
        Producer sends message to queue.
        NON-BLOCKING - producer continues immediately.
        Message persisted for fault tolerance.
        """
        with self._lock:
            if queue_name not in self._queues:
                self.create_queue(queue_name)
            if self._sequence_counter.get(queue_name, 0) == 0:
                self._sequence_counter[queue_name] = 0
            self._sequence_counter[queue_name] += 1
            message.sequence_number = self._sequence_counter[queue_name]
            if message.persist:
                self._persistent_store[queue_name].append(message)
            self._queues[queue_name].append(message)
            self._sent_count += 1
            self._message_log.append(
                {"action": "sent", "queue": queue_name, "msg_id": message.message_id}
            )

        print(f"[ASYNC] {message.sender_id} → Queue:{queue_name} | {message.message_type.value} | ID:{message.message_id}")
        print(f"        Producer continues without waiting ✓")
        return True

    def receive(
        self,
        queue_name: str,
        consumer_id: str,
        timeout: float = 0.1,
    ) -> Message | None:
        """
        Consumer polls queue when ready.
        Returns message or None if queue empty.
        Consumer controls when it receives - load leveling.
        """
        with self._lock:
            if queue_name not in self._queues or not self._queues[queue_name]:
                return None
            message = self._queues[queue_name].popleft()
            message.status = MessageStatus.DELIVERED
            self._delivered_ids.add(message.message_id)
            self._delivered_count += 1
            self._message_log.append(
                {"action": "delivered", "queue": queue_name, "msg_id": message.message_id}
            )

        print(f"[QUEUE] {consumer_id} polling {queue_name}...")
        print(f"[DELIVERED] Message {message.message_id} → {consumer_id}")
        return message

    def send_response(
        self,
        queue_name: str,
        original_message: Message,
        response_payload: dict,
        responder_id: str,
    ) -> Message:
        """
        Send correlated response.
        Response shares correlation_id with original request.
        """
        if not original_message.correlation_id:
            original_message.correlation_id = str(uuid.uuid4())[:8]
        response = Message(
            message_id=str(uuid.uuid4())[:8],
            correlation_id=original_message.correlation_id,
            message_type=MessageType.RESPONSE,
            sender_id=responder_id,
            recipient_id=original_message.sender_id,
            payload=response_payload,
            status=MessageStatus.QUEUED,
        )
        with self._lock:
            if queue_name not in self._response_store:
                self._response_store[queue_name] = []
            self._response_store[queue_name].append(response)
            self._sent_count += 1

        print(f"[RESPONSE] {responder_id} → Queue | Correlation:{response.correlation_id}")
        return response

    def receive_response(
        self,
        queue_name: str,
        correlation_id: str,
        consumer_id: str,
    ) -> Message | None:
        """
        Receive response matching a correlation_id.
        Consumer only gets the response for ITS request.
        """
        with self._lock:
            if queue_name not in self._response_store:
                return None
            for i, response in enumerate(self._response_store[queue_name]):
                if response.correlation_id == correlation_id:
                    self._response_store[queue_name].pop(i)
                    self._delivered_count += 1
                    print(f"[MATCHED] {consumer_id} receives response for {correlation_id} ✅")
                    return response
        return None

    def simulate_failure_and_recovery(self, queue_name: str):
        """
        Simulate queue crash and recovery.
        Show messages are NOT lost (persistence).
        """
        with self._lock:
            if queue_name not in self._persistent_store:
                return
            print(f"[FAILURE] Queue {queue_name} crashed!")
            # Simulate: clear in-memory queue
            self._queues[queue_name] = deque()
            # Recover from persistence (only undelivered)
            for msg in self._persistent_store[queue_name]:
                if msg.message_id not in self._delivered_ids:
                    self._queues[queue_name].append(msg)
            recovered = len(self._queues[queue_name])
        print(f"[RECOVERY] Queue {queue_name} restored: {recovered} messages recovered")

    def get_queue_depth(self, queue_name: str) -> int:
        """Number of messages waiting in queue."""
        with self._lock:
            if queue_name not in self._queues:
                return 0
            return len(self._queues[queue_name])

    def get_pending_responses(self, queue_name: str) -> int:
        """Number of responses waiting."""
        with self._lock:
            if queue_name not in self._response_store:
                return 0
            return len(self._response_store[queue_name])

    def get_stats(self) -> dict:
        """Full stats: sent, delivered, pending, failed."""
        with self._lock:
            total_pending = sum(len(q) for q in self._queues.values())
            return {
                "sent": self._sent_count,
                "delivered": self._delivered_count,
                "failed": self._failed_count,
                "pending": total_pending,
            }
