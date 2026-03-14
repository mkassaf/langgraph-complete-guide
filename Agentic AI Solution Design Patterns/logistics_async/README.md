# Logistics Async Messaging — Fleet Management Demo

Demonstrates the **full async messaging scenario** from the lesson: 4 AI agents managing a truck delivery fleet via a central message queue.

## Scenario

- **New Order Agent**: Receives orders (PRODUCER), polls for fulfillment (CONSUMER)
- **Route Optimization Agent**: Polls for orders, calculates routes (CONSUMER → PRODUCER)
- **Vehicle Assignment Agent**: Polls for routes, assigns truck+driver (CONSUMER → PRODUCER)
- **Dispatch Agent**: Polls for assignments, dispatches to truck/driver (CONSUMER → PRODUCER)

**Correlation ID** tracks each order from start to finish (same ID for all messages in one order).

## Setup

```bash
pip install anthropic python-dotenv
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

## Run

```bash
cd "Agentic AI Solution Design Patterns/logistics_async"
python main.py
```

*Note: ~12 LLM calls; may take 1–2 minutes.*
