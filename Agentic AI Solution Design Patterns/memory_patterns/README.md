# Memory, Skill & Adaptive Action Patterns

Meeting planning assistant that learns and improves over time.

## Patterns

1. **Episodic + Procedural Memory** — Store user interactions and action outcomes. Episodic: preferences, feedback. Procedural: tool sequences, latencies, skill templates.

2. **In-Context Learning** — Retrieve relevant memories and inject into prompts. Clear BEFORE/AFTER: without memory (slow, no preferences) vs with memory (fast, 100% preference match).

3. **Adaptive Tool Orchestration** — LLM defines toolchain; orchestrator executes it without LLM. Trade-off: efficient but less adaptive.

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
memory_patterns/
├── config.py
├── memory/           # vector_db, episodic_store, procedural_store, memory_module
├── tools/            # calendar, venue, catering, booking
├── patterns/         # episodic_procedural, in_context_learning, adaptive_orchestration
├── agents/           # orchestrator_module
├── prompts.py
├── llm_client.py
└── main.py
```
