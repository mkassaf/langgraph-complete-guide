# Tool Discovery and Use — Office Building Demo

Demonstrates the **Tool Discovery and Use** design pattern: an agent with 24 tools discovers the right ones dynamically instead of loading all upfront.

## Scenario

An office building agent must complete various tasks. It has access to 24 tools but cannot load all into the context window. It must **discover** the right tools based on current needs.

## Two Modes

1. **All Tools Upfront** — Load all 24 tool descriptions into the prompt (inefficient, ~4000+ tokens)
2. **Dynamic Discovery** — Start with registry summary (~300 tokens), discover tools on demand

## Setup

1. `pip install anthropic python-dotenv`
2. Add `ANTHROPIC_API_KEY` to `.env`

## Run

```bash
python "Agentic AI Solution Design Patterns/tool_discovery/main.py"
```

## Project Structure

```
tool_discovery/
├── config.py
├── registry/
│   ├── tool_spec.py
│   ├── tool_registry.py      # discover_tools(need="...")
│   └── registry_builder.py  # 24 tools across 6 categories
├── tools/
│   └── impl.py              # Simulated tool implementations
├── prompts.py
├── llm_client.py
├── controller.py
├── agent.py
└── main.py
```

## Categories

- **booking** (4): room, desk, parking, equipment
- **IT** (5): ticket, password, software, VPN, hardware
- **facilities** (6): maintenance, cleaning, temperature, lighting, printer, supplies
- **admin** (4): visitor, access, expense, HR
- **security** (3): incident, CCTV, lost/found
- **catering** (2): catering order, coffee machine
