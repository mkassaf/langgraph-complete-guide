# Planning Pattern — Orchestrator-Worker Demo

Demonstrates the **Planning design pattern** (Orchestrator-Worker) for organizing a large company event. An Orchestrator breaks the task into subtasks and delegates to specialized Workers.

## Scenario

Plan a company annual conference for 500 people:
- 2-day event, $150k budget
- Venue, registration, catering, speakers, marketing

## Three Phases

1. **Task Decomposition:** Orchestrator LLM breaks task into 5 work units
2. **Worker Execution:** Each worker handles its domain (venue, registration, etc.)
3. **Result Synthesis:** Orchestrator LLM combines results into final plan

## Setup

1. `pip install anthropic python-dotenv`
2. Add `ANTHROPIC_API_KEY` to `.env`

## Run

```bash
python "Agentic AI Solution Design Patterns/planning_pattern/main.py"
```

## Project Structure

```
planning_pattern/
├── config.py
├── prompts.py
├── llm_client.py
├── agents/
│   ├── base_agent.py
│   ├── orchestrator/
│   │   ├── task_decomposer.py
│   │   └── orchestrator_agent.py
│   └── workers/
│       ├── venue_worker.py
│       ├── registration_worker.py
│       ├── catering_worker.py
│       ├── speakers_worker.py
│       └── marketing_worker.py
├── communication/
│   ├── work_unit.py
│   └── message_bus.py
└── main.py
```

## Key Insight

Orchestrator maintains high-level coherence while workers handle details with focused context, preventing context window overflow.
