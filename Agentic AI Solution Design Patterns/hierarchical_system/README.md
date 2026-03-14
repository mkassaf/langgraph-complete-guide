# Hierarchical Multi-Agent System — Global Product Launch Demo

Demonstrates the **Hierarchical Multi-Agent System** pattern with a 3-layer hierarchy for a global product launch.

## Scenario

Launch CloudSync Pro v2.0 globally:
- 3 regions: Americas, Europe, Asia-Pacific
- 6-month timeline, $5M budget
- Development, Marketing, Operations domains

## 3-Layer Hierarchy

| Layer | Type | Agents |
|-------|------|--------|
| **Layer 1** | Utility-Based | Main Orchestrator |
| **Layer 2** | Goal-Based | Development, Marketing, Operations Sub-Orchestrators |
| **Layer 3** | Reflex + Expert Teams | 6 Workers + 2 Expert Teams |

## Flow

1. **Layer 1** creates high-level plan, delegates to 3 sub-orchestrators
2. **Layer 2** breaks domain goals into tasks, delegates to workers
3. **Layer 3** executes tasks (workers + expert teams collaborate internally)
4. Results flow back up: L3 → L2 → L1
5. **Layer 1** synthesizes final executive report

## Setup

1. `pip install anthropic python-dotenv`
2. Add `ANTHROPIC_API_KEY` to `.env`

## Run

```bash
python "Agentic AI Solution Design Patterns/hierarchical_system/main.py"
```

## Project Structure

```
hierarchical_system/
├── config.py
├── prompts.py
├── llm_client.py
├── layers/
│   ├── layer1_orchestrator/
│   ├── layer2_sub_orchestrators/
│   └── layer3_workers/
│       ├── dev_workers/
│       ├── marketing_workers/
│       ├── ops_workers/
│       └── expert_teams/
├── communication/
│   ├── message_router.py
│   └── hierarchy_tracker.py
└── main.py
```

## Key Insight

No single agent is overwhelmed. Each layer handles appropriate complexity. Layer 1 never communicates directly with Layer 3—all messages go through the hierarchy.
