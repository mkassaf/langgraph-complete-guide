# Knowledge Graph Integration — Office Building Demo

Demonstrates the **Knowledge Graph Integration** design pattern using the Anthropic Claude API in a smart office building scenario.

## Scenario

An office building AI agent answers questions about rooms, equipment, and people. The demo shows:

1. **Without Knowledge Graph** — LLM relies on training data (may hallucinate, e.g. printer in Room 301)
2. **With Knowledge Graph** — LLM uses graph data (accurate, e.g. printer in Room 303)

**Key test**: Printer was recently moved from Room 301 → Room 303. This change is NOT in LLM training data.

## Setup

1. `pip install anthropic python-dotenv`
2. Add `ANTHROPIC_API_KEY` to `.env`

## Run

```bash
python "Agentic AI Solution Design Patterns/knowledge_graph/main.py"
```

## Project Structure

```
knowledge_graph/
├── config.py
├── graph/
│   ├── knowledge_graph.py   # Entities, relationships, query, find_path
│   ├── graph_builder.py     # Builds graph, simulate_recent_change
│   └── graph_query_tool.py  # Natural language query interface
├── prompts.py
├── llm_client.py
├── controller.py
├── agent.py
└── main.py
```

## Test Questions

- Where is the printer located?
- What paper does the printer use and where is it stored?
- Who should I contact if the printer breaks?
- What equipment is available in room 303?
- How do I get from the printer to the paper supply?

## Hallucination Detection

Simple string comparison: if LLM says "301" but graph says "303" for printer location → flag as hallucination.
