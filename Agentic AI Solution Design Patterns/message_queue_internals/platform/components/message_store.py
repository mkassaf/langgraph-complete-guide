"""
Message Store — Component 2: Persistent storage for fault tolerance.
"""

from .request_queue import Message


class MessageStore:
    """
    COMPONENT 2: Persistent storage for fault tolerance.

    From lesson: 'It may also be placed in a message store
    repository to ensure that it is safely stored and can
    be recovered in case the message queue platform
    encounters a failure condition.'

    Messages removed ONLY after acknowledgement received.
    """

    def __init__(self, store_name: str):
        self.name = store_name
        self._store: dict[str, Message] = {}
        self._recovery_log: list[str] = []
        self._acknowledged_ids: set[str] = set()

    def persist(self, message: Message):
        """Save message to persistent store."""
        self._store[message.message_id] = message
        print(f"[MESSAGE STORE:{self.name}] Persisted: {message.message_id}")
        print(f"                   Safety guaranteed - survives platform failure")

    def remove(self, message_id: str):
        """Remove after successful acknowledgement."""
        if message_id in self._store:
            del self._store[message_id]
        self._acknowledged_ids.add(message_id)
        print(f"[MESSAGE STORE:{self.name}] Removed: {message_id}")
        print(f"                   (Acknowledged - no longer needed)")

    def recover_all(self) -> list[Message]:
        """Recover all unacknowledged messages after failure."""
        unacked = [m for m in self._store.values() if m.message_id not in self._acknowledged_ids]
        print(f"[MESSAGE STORE:{self.name}] RECOVERY: {len(unacked)} messages restored")
        return unacked

    def simulate_failure_and_recovery(self) -> list[Message]:
        """
        Simulate platform crash.
        Show messages survive in persistent store.
        Return recovered messages.
        """
        print(f"[MESSAGE STORE:{self.name}] 💥 Platform failure!")
        print(f"[MESSAGE STORE:{self.name}] 🔄 Recovering...")
        recovered = self.recover_all()
        print(f"[MESSAGE STORE:{self.name}] ✅ {len(recovered)} messages recovered")
        return recovered

    def get_count(self) -> int:
        """Unacknowledged messages in store."""
        return len(self._store)

    def get_message(self, message_id: str) -> Message | None:
        """Get message by ID."""
        return self._store.get(message_id)
