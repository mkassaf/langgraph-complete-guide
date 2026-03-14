"""
Response Queue — Component 5: Holds response messages.
"""

from .request_queue import Message


class ResponseQueue:
    """
    COMPONENT 5: Holds response messages.

    From lesson: 'If a response message is necessary,
    the original consumer service then assumes the role
    of the producer... This message is sent to a separate
    response queue and is stored the same way as before.'

    Separate from request queue.
    Uses same correlation_id as original request.
    """

    def __init__(self):
        self._queue: list[Message] = []

    def enqueue_response(self, response: Message):
        """Add response message. Verify it has correlation_id matching a request."""
        self._queue.append(response)
        print(f"[RESPONSE QUEUE]   Response enqueued")
        print(f"                   Correlation: {response.correlation_id} (links to original request)")
        print(f"                   From: {response.sender_id} → To: {response.recipient_id}")

    def dequeue_for_correlation(
        self,
        correlation_id: str,
    ) -> Message | None:
        """Get response matching specific correlation_id."""
        for i, msg in enumerate(self._queue):
            if msg.correlation_id == correlation_id:
                self._queue.pop(i)
                print(f"[RESPONSE QUEUE]   Response found for {correlation_id}")
                return msg
        return None

    def size(self) -> int:
        """Responses waiting."""
        return len(self._queue)
