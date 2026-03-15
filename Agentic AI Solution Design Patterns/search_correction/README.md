# Search and Self-Correction Patterns

Three patterns for the same task: organize a half-day team meeting for 15 people in 3 weeks. Each pattern handles errors and finds optimal solutions differently.

## Patterns

1. **LATS (Language Agent Tree Search)** — MCTS-based search. Generates multiple candidate actions, evaluates via 4-phase loop (Selection, Expansion, Simulation, Back-propagation), selects best atomic action.

2. **Self-Discover** — Stage 1: Meta-controller discovers optimal reasoning rules. Stage 2: Execute with those rules embedded. Strategy before execution.

3. **Second-Pass Verification** — Planner generates plan. Independent verifier LLM checks (sequence, vendor compliance, etc.). Planner revises if fail. Two rounds: errors injected → caught → fixed.

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
search_correction/
├── config.py
├── tools/           # calendar, venue, catering, compliance_checker
├── patterns/        # LATS, Self-Discover, Verification
├── shared/          # MCTS tree, meta-controller
├── prompts.py
├── llm_client.py
└── main.py
```
