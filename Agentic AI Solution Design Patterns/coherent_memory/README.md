# Coherent State and Collective Memory — Warehouse Demo

Demonstrates the **Coherent State and Collective Memory** pattern in a multi-agent warehouse order fulfillment system.

## Scenario

4 warehouse agents collaborate on order #ORD-2847:
- **Inventory** — reserves stock
- **Picking** — picks items from shelves
- **Packing** — packs into boxes
- **Shipping** — arranges shipment

## Two Modes

### WITHOUT Shared Memory
- Inventory reserves (private only) → picking doesn't know
- Picking duplicates work (no visibility)
- Packing starts before picking completes (race)
- Shipping uses stale order data
- **Result: FAILED**

### WITH Shared Memory
- Inventory writes reservations to shared memory
- Picking reads reservations, no duplication
- Packing waits for picking status in shared memory
- Shipping reads complete status
- **Result: SUCCESS**

## Setup

1. `pip install anthropic python-dotenv`
2. Add `ANTHROPIC_API_KEY` to `.env`

## Run

```bash
python "Agentic AI Solution Design Patterns/coherent_memory/main.py"
```

## Project Structure

```
coherent_memory/
├── config.py
├── memory/
│   ├── memory_types.py
│   ├── shared_memory.py
│   └── agent_memory.py
├── agents/
│   ├── inventory_agent.py
│   ├── picking_agent.py
│   ├── packing_agent.py
│   └── shipping_agent.py
├── scenarios/
│   ├── without_shared_memory.py
│   └── with_shared_memory.py
├── prompts.py
├── llm_client.py
└── main.py
```

## Key Insight

Shared memory is the foundation that makes multi-agent patterns work correctly at scale.
