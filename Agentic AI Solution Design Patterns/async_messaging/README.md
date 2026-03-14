# Asynchronous Messaging Architecture — Order Processing Demo

Demonstrates **async messaging patterns** in a multi-agent e-commerce order processing system.

## Patterns Demonstrated

1. **Decoupled Task Deferral** — Producer sends without waiting
2. **Consumer Load Leveling** — Queue buffers messages; consumers process at own pace
3. **Reliable Communication** — Persistence survives simulated failure
4. **Async Request-Response** — Correlation IDs link requests to responses
5. **Sequential FIFO Processing** — Orders fulfilled in exact queue order

Also: **Sync vs Async comparison** and **intra-agent lightweight broker**.

## Setup

```bash
pip install anthropic python-dotenv
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

## Run

```bash
cd "Agentic AI Solution Design Patterns/async_messaging"
python main.py
```

*Note: Demo makes ~20 LLM calls; may take 1–2 minutes.*

## Architecture

- **MessageQueuePlatform** — Full-featured broker with persistence, correlation, FIFO
- **LightweightBroker** — In-memory intra-agent queue (no persistence)
- **Agents** — Order (producer), Inventory, Payment, Fulfillment (consumers)
