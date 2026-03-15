# Planning & Execution Patterns

Four design patterns for the same task: plan a half-day team offsite for 15 people with engaging activities and catering.

## Patterns

1. **Plan-and-Execute** — Separate planning (LLM once) and execution (no LLM). Simple, low cost.
2. **Concurrent Optimizer** — Task compiler builds DAG; independent steps run in parallel.
3. **Reasoning Without Observation** — All reasoning before any tool calls; parallel data retrieval; synthesis.
4. **Planner-Critic-Refiner** — Planner → Critic → Refiner loop until quality threshold.

## Setup

```bash
pip install -r requirements.txt
```

Set `ANTHROPIC_API_KEY` in `.env`.

## Run

```bash
python main.py
```

## Project Structure

```
planning_patterns/
├── config.py
├── tools/           # calendar, venue, catering, document (simulated)
├── patterns/        # 4 pattern implementations
├── shared/          # DAG, task compiler, synthesis template
├── prompts.py
├── llm_client.py
└── main.py
```
