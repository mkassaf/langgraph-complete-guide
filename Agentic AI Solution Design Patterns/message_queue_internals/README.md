# Message Queue Internals — Component Demonstration

Demonstrates **all 6 internal components** of a Message Queue platform working together.

## Components

1. **Request Queue** — Holds incoming request messages
2. **Message Store** — Persistent storage for fault tolerance
3. **Request Dispatcher** — Sends messages to ready consumers
4. **Ack Handler** — Handles delivery acknowledgements
5. **Response Queue** — Holds response messages
6. **Response Dispatcher** — Sends responses back to original producers

## Scenario

Two AI agents (OrderAgent, FulfillmentAgent) communicate through the platform:
- **OrderAgent**: Producer → sends orders; Consumer → receives fulfillment responses
- **FulfillmentAgent**: Consumer → receives orders, acks; Producer → sends fulfillment responses

## Setup

```bash
pip install anthropic python-dotenv
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

## Run

```bash
cd "Agentic AI Solution Design Patterns/message_queue_internals"
python main.py
```
