# Event-Driven Learning Platform

Demonstrates **Event-Driven Architecture for Agentic AI** using the Anthropic Claude API for an online learning platform.

## Architecture

- **4 agents** + central event hub
- **NO direct agent-to-agent communication** — events drive ALL system behavior

### Event Chain

1. **① LEARNING_INTERACTION** — User Activity Agent (producer only)
2. **② SKILL_GAP_DETECTED** — Performance Agent (consumer ① → producer ②)
3. **③ RECOMMENDATION_READY** — Content Agent (consumer ② → producer ③)
4. **Interface Agent** — Consumer of both ② and ③ (different reactions)

### Agents

| Agent | Role | Subscribes to | Publishes |
|-------|------|---------------|-----------|
| User Activity | Producer | — | ① |
| Performance | Consumer→Producer | ① | ② |
| Content | Consumer→Producer | ② | ③ |
| Interface | Consumer | ②, ③ | — |

## Setup

```bash
pip install -r requirements.txt
```

Set `ANTHROPIC_API_KEY` in `.env` (or use `../../.env` from project root).

## Run

```bash
python main.py
```

## Project Structure

```
learning_platform/
├── config.py
├── event_hub/event_hub.py
├── agents/
│   ├── user_activity_agent.py
│   ├── performance_agent.py
│   ├── content_agent.py
│   └── interface_agent.py
├── data/
│   ├── student_data.py
│   └── content_library.py
├── prompts.py
├── llm_client.py
└── main.py
```
