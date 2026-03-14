"""
Shared memory system — central Single Source of Truth.
"""

from datetime import datetime

from memory.memory_types import StateCategory, StateEntry, SharedMemorySnapshot


class SharedMemorySystem:
    """
    Central shared memory - Single Source of Truth.

    ALL agents read from and write to this system.
    Prevents conflicting/outdated information.
    """

    def __init__(self):
        self.store: dict[str, StateEntry] = {}
        self.subscribers: dict[str, list[str]] = {}
        self.event_log: list[dict] = []
        self._read_count = 0
        self._write_count = 0

    def write(
        self,
        key: str,
        value: dict | str | int | float,
        category: StateCategory,
        written_by: str,
    ) -> StateEntry:
        """Agent writes state update to shared memory."""
        version = 1
        if key in self.store:
            version = self.store[key].version + 1

        entry = StateEntry(
            key=key,
            value=value,
            category=category,
            written_by=written_by,
            timestamp=datetime.now().isoformat(),
            version=version,
        )
        self.store[key] = entry
        self._write_count += 1
        self.event_log.append({
            "type": "write",
            "key": key,
            "by": written_by,
            "timestamp": entry.timestamp,
        })
        return entry

    def read(self, key: str, requesting_agent: str) -> StateEntry | None:
        """Agent reads current state from shared memory."""
        self._read_count += 1
        self.event_log.append({
            "type": "read",
            "key": key,
            "by": requesting_agent,
            "timestamp": datetime.now().isoformat(),
        })
        return self.store.get(key)

    def read_by_category(
        self,
        category: StateCategory,
        requesting_agent: str,
    ) -> list[StateEntry]:
        """Get all entries in a category."""
        result = [e for e in self.store.values() if e.category == category]
        self._read_count += len(result)
        for e in result:
            self.event_log.append({
                "type": "read",
                "key": e.key,
                "by": requesting_agent,
                "timestamp": datetime.now().isoformat(),
            })
        return result

    def subscribe(self, key: str, agent_id: str):
        """Agent subscribes to updates on a key."""
        if key not in self.subscribers:
            self.subscribers[key] = []
        if agent_id not in self.subscribers[key]:
            self.subscribers[key].append(agent_id)

    def get_snapshot(self) -> SharedMemorySnapshot:
        """Get full current state of shared memory."""
        last_by = ""
        last_ts = ""
        for e in self.store.values():
            if e.timestamp > last_ts:
                last_ts = e.timestamp
                last_by = e.written_by
        return SharedMemorySnapshot(
            timestamp=datetime.now().isoformat(),
            entries=dict(self.store),
            total_entries=len(self.store),
            last_updated_by=last_by,
        )

    def get_event_log(self) -> list[dict]:
        """Get full history of reads and writes."""
        return list(self.event_log)

    def get_read_count(self) -> int:
        return self._read_count

    def get_write_count(self) -> int:
        return self._write_count
