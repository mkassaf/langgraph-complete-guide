"""
Response Dispatcher — Component 6: Sends responses back to original producers.
"""

from .request_queue import Message
from .response_queue import ResponseQueue


class ResponseDispatcher:
    """
    COMPONENT 6: Sends responses back to original producers.

    From lesson: 'It is then sent to microservice A via
    a separate response dispatcher component.'

    Mirror of RequestDispatcher but for responses.
    Uses correlation_id to route to correct original sender.
    """

    def __init__(self):
        self._waiting_producers: dict[str, str] = {}  # correlation_id → producer_id

    def register_producer_waiting(
        self,
        producer_id: str,
        correlation_id: str,
    ):
        """Producer registers that it's waiting for a response."""
        self._waiting_producers[correlation_id] = producer_id
        print(f"[RESPONSE DISP.]   {producer_id} waiting for")
        print(f"                   response to correlation: {correlation_id}")

    def dispatch_response(
        self,
        response_queue: ResponseQueue,
        correlation_id: str | None = None,
    ) -> tuple[Message | None, str]:
        """
        Send response to waiting producer.
        Match using correlation_id.
        If correlation_id given, only match that. Else try any waiting producer.
        """
        ids_to_try = [correlation_id] if correlation_id else list(self._waiting_producers.keys())
        for corr_id in ids_to_try:
            if corr_id not in self._waiting_producers:
                continue
            producer_id = self._waiting_producers[corr_id]
            response = response_queue.dequeue_for_correlation(corr_id)
            if response:
                del self._waiting_producers[corr_id]
                print(f"[RESPONSE DISP.]   Dispatching response")
                print(f"                   Correlation: {corr_id} → {producer_id}")
                print(f"                   Original request-response cycle complete ✓")
                return (response, producer_id)
        return (None, "")
