# ReAct Pattern — Meeting Planner Demo

Demonstrates the **ReAct (Reasoning + Acting)** design pattern using the Anthropic Claude API, applied to a meeting planning scenario.

## Scenario

An AI agent plans a half-day team offsite meeting for 15 people next month. Unlike Chain of Thought (text only), this agent **actually performs actions** using tools and adapts based on results.

## Setup

1. Install: `pip install anthropic python-dotenv`
2. Add `ANTHROPIC_API_KEY` to `.env` (project root)

## Run

From project root:
```bash
python "Agentic AI Solution Design Patterns/react_pattern/main.py"
```

Or:
```bash
cd "Agentic AI Solution Design Patterns/react_pattern"
python main.py
```

## Project Structure

```
react_pattern/
├── config.py       # API config, user request
├── prompts.py      # ReAct system prompt
├── tools/
│   ├── base_tool.py    # Abstract tool class
│   ├── calendar_tool.py   # Check team availability
│   ├── venue_tool.py      # Search venues
│   ├── catering_tool.py   # Get catering options
│   └── document_tool.py   # Create proposal.md
├── llm_client.py   # Anthropic API wrapper
├── controller.py   # Controller module (intermediary)
├── agent.py        # MeetingPlannerAgent
└── main.py         # Entry point
```

## ReAct Loop

1. **THOUGHT** — LLM reasons about next step
2. **ACTION** — LLM outputs tool call
3. **OBSERVATION** — Tool result fed back to LLM
4. Repeat until **FINAL** or max iterations

## Design Pattern

- **Controller**: Intermediary between LLM and tools; parses actions, routes to tools, maintains conversation history
- **LLM**: Reasoning module; outputs THOUGHT + ACTION
- **Tools**: ACTION layer; calendar, venue, catering, document (simulated)
