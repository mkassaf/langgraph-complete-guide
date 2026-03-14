"""
Ack Handler — Component 4: Handles delivery acknowledgements.
"""

from .message_store import MessageStore


class AckHandler:
    """
    COMPONENT 4: Handles delivery acknowledgements.

    From lesson: 'The consumer then replies with an
    acknowledgement to confirm receipt of the message.
    This is sent to a separate acknowledgement handler
    inside the message queue platform. Upon receiving
    this acknowledgement, the message is typically
    removed from the message store.'
    """

    def __init__(self, message_store: MessageStore):
        self.store = message_store
        self.ack_log: list[dict] = []

    def receive_ack(
        self,
        message_id: str,
        consumer_id: str,
    ):
        """Process acknowledgement from consumer. Remove message from persistent store."""
        self.ack_log.append({"message_id": message_id, "consumer_id": consumer_id})
        print(f"[ACK HANDLER]      Acknowledgement received")
        print(f"                   Message: {message_id} | From: {consumer_id}")
        print(f"                   Removing from message store... ✓")
        self.store.remove(message_id)

    def get_ack_count(self) -> int:
        """Total acknowledgements processed."""
        return len(self.ack_log)
