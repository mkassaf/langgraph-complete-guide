"""
Request Dispatcher — Component 3: Sends messages to ready consumers.
"""

from .request_queue import RequestQueue, Message


class RequestDispatcher:
    """
    COMPONENT 3: Sends messages to ready consumers.

    From lesson: 'When the target consumer is ready to
    receive the message, a request dispatcher component
    retrieves it from the queue and sends it.'

    Key behavior: Only dispatches when consumer is connected
    and polling. Monitors consumer connection status.
    """

    def __init__(self):
        self._connected_consumers: dict[str, bool] = {}
        self._dispatch_log: list[dict] = []
        self._target_recipient: str = ""

    def consumer_connects(self, consumer_id: str):
        """Consumer establishes polling connection."""
        self._connected_consumers[consumer_id] = True
        print(f"[REQUEST DISP.]    {consumer_id} connected")
        print(f"                   Now polling for messages...")

    def consumer_disconnects(self, consumer_id: str):
        """Consumer goes offline."""
        self._connected_consumers[consumer_id] = False
        print(f"[REQUEST DISP.]    {consumer_id} disconnected")
        print(f"                   Messages will be held until reconnection")

    def is_consumer_ready(self, consumer_id: str) -> bool:
        """Check if specific consumer is connected and polling."""
        return self._connected_consumers.get(consumer_id, False)

    def dispatch(
        self,
        request_queue: RequestQueue,
    ) -> tuple[Message | None, str]:
        """
        Attempt to dispatch next queued message.

        If consumer ready:
          - Dequeue message
          - Send to consumer
          - Print delivery confirmation

        If consumer not ready:
          - Hold in queue
          - Print held message
        """
        msg = request_queue.peek()
        if not msg:
            return (None, "")
        recipient = msg.recipient_id
        if self.is_consumer_ready(recipient):
            msg = request_queue.dequeue()
            if msg:
                self._dispatch_log.append({"message_id": msg.message_id, "consumer": recipient})
                print(f"[REQUEST DISP.]    Dispatching {msg.message_id} → {recipient}")
                print(f"                   Consumer was polling - message delivered ✓")
                return (msg, recipient)
        else:
            depth = request_queue.size()
            print(f"[REQUEST DISP.]    {recipient} not ready")
            print(f"                   Message held in queue (depth: {depth})")
        return (None, "")
