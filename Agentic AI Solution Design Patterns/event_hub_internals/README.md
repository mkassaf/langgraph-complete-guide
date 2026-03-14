# Event Hub Internals — Smart Factory Demo

Demonstrates **all internal components** of an Event Hub platform.

## Components

1. **Event Receiver** — Accepts incoming events from producers
2. **Storage Repository** — Long-term event storage with channel partitions
3. **Channel Partition** — Events persist (NEVER deleted) for replay
4. **Controller Component** — Manages channel metadata
5. **Group Coordinator** — Manages subscriber groups, ready/offline status
6. **Dispatch Function** — Sends to ready consumers, queues for offline

## Key Difference from Message Queue

- Events **NOT deleted** after delivery
- Long-term retention for multiple subscribers + replay
- Offline consumers receive events when they poll

## Agents

- **Sensor Agent** (PRODUCER): Publishes factory events
- **Maintenance Agent** (CONSUMER): Machine + quality events
- **Safety Agent** (CONSUMER): Safety + machine events (starts offline)
- **Analytics Agent** (CONSUMER): Batch stream + replay

## Setup

```bash
pip install anthropic python-dotenv
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

## Run

```bash
cd "Agentic AI Solution Design Patterns/event_hub_internals"
python main.py
```
