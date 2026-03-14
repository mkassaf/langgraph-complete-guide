# Human-in-the-Loop — Warehouse Robot Demo

Demonstrates the **Human-in-the-Loop** design pattern: a warehouse robot encounters an unexpected locked door, requests human help, learns a new skill from demonstration, and applies it independently next time.

## Three Scenarios

1. **Normal Task (Room 301)** — Unlocked door, existing skill, no human needed
2. **Unexpected Obstacle (Room 303)** — Locked door with keypad, robot requests human, human demonstrates, robot learns `use_keypad_door`
3. **Same Door Again (Room 303)** — Robot uses learned skill, no human needed

## Setup

1. `pip install anthropic python-dotenv`
2. Add `ANTHROPIC_API_KEY` to `.env`

## Run

```bash
python "Agentic AI Solution Design Patterns/human_in_loop/main.py"
```

## Project Structure

```
human_in_loop/
├── config.py
├── prompts.py
├── environment/
│   └── warehouse.py      # Rooms, doors, delivery tasks
├── human/
│   ├── human_supervisor.py   # Receives alerts, responds
│   └── teaching_session.py   # Demonstrates keypad entry
├── agent/
│   ├── skill_library.py  # Stores skills, learn_new_skill()
│   ├── llm_client.py
│   └── controller.py    # assess, request_human, learn, execute
├── agent.py
└── main.py
```

## Key Insight

Human-in-the-Loop doesn't just solve the immediate problem — it permanently expands the agent's capabilities for future tasks.
