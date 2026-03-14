# Event-Driven Architecture — Smart City Demo

Demonstrates **Event-Driven Architecture** for Agentic AI in a smart city monitoring scenario.

## Patterns Demonstrated

1. **Situational Awareness** — Agents react to environment changes in real time
2. **Broadcasting** — One event → multiple independent reactions (FIRE → emergency + maintenance)
3. **Reaction Triggers** — Events drive system behavior
4. **Stream Processing** — Continuous event flow analytics
5. **Event Replay** — Historical event reprocessing for pattern analysis
6. **Intra-Agent** — Internal event bus within city_monitor_agent

## Agents

- **City Monitor** (PRODUCER): Detects events via sensors, publishes to Event Hub
- **Traffic Agent** (CONSUMER): Reacts to traffic_jam, accident, road_closure
- **Emergency Agent** (CONSUMER): Reacts to fire, medical, crime, accident
- **Maintenance Agent** (CONSUMER): Reacts to power, water, streetlight, fire
- **Analytics Agent** (CONSUMER): Stream processing + event replay

## Setup

```bash
pip install anthropic python-dotenv
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

## Run

```bash
cd "Agentic AI Solution Design Patterns/event_driven"
python main.py
```

*Note: ~15 LLM calls; may take 1–2 minutes.*
