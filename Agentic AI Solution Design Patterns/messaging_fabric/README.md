# Messaging Fabric Platforms — Smart Factory Demo

Demonstrates all three **Messaging Fabric Platforms** in an agentic AI smart factory:

1. **Message Queue** — Point-to-point sequential production tasks
2. **Event Hub** — Publish-subscribe factory-wide alert broadcasting
3. **Batch Queue** — End-of-shift quality report aggregation

## Setup

```bash
# From project root
pip install anthropic python-dotenv

# Set API key in .env (or parent .env)
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

## Run

```bash
cd "Agentic AI Solution Design Patterns/messaging_fabric"
python main.py
```

## Architecture

- **Platforms** (`platforms/`): Message Queue, Event Hub, Batch Queue
- **Fabric** (`fabric/`): Unified interface; agents use fabric, not platforms directly
- **Agents** (`agents/`): Production, Quality, Maintenance, Safety, Report — each uses the appropriate platform via the fabric
