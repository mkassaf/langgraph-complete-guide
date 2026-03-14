# Specialized Expert Team Pattern — Breach Response Demo

Demonstrates the **Specialized Expert Team** pattern: multiple expert agents collaborate deeply on a cybersecurity breach. The team appears as a single worker to an orchestrator.

## Scenario

- Unauthorized access in customer database
- 50K records potentially exposed
- SQL injection via web portal
- Attack appears ongoing

## Flow

1. **Orchestrator** delegates breach response as ONE subtask
2. **Entry point** receives task, coordinates 4 experts
3. **Round 0:** Each expert does independent initial analysis
4. **Rounds 1–3:** Experts share, challenge, debate findings
5. **Consensus:** Unified response returned to orchestrator

## Experts

- 🔐 **Threat analyst** — attack vectors, threat actors
- 🌐 **Network expert** — damage assessment, containment
- ⚖️ **Legal advisor** — GDPR, liability, notification
- 📣 **Comms manager** — stakeholder messaging

## Setup

1. `pip install anthropic python-dotenv`
2. Add `ANTHROPIC_API_KEY` to `.env`

## Run

```bash
python "Agentic AI Solution Design Patterns/expert_team/main.py"
```

## Project Structure

```
expert_team/
├── config.py
├── prompts.py
├── llm_client.py
├── orchestrator/
│   └── crisis_orchestrator.py
├── expert_team/
│   ├── entry_point.py
│   ├── collaboration_bus.py
│   ├── consensus_builder.py
│   └── experts/
│       ├── base_expert.py
│       ├── threat_analyst.py
│       ├── network_expert.py
│       ├── legal_advisor.py
│       └── comms_manager.py
└── main.py
```

## Key Insight

The expert team produces a response that no single agent could create—it requires deep domain expertise and cross-domain collaboration.
