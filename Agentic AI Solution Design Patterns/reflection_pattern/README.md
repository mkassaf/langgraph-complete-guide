# Reflection Pattern — Meeting Planner Demo

Demonstrates the **Reflection** design pattern combined with Chain of Thought and ReAct, using the Anthropic Claude API.

## Three Modes

1. **CoT + Reflection** — Improve text output before releasing (completeness, assumptions, logic)
2. **ReAct + Reflection** — Detect and fix errors after actions (document_tool fails → correction applied)
3. **Pattern Switch** — Simple prompt → reflection recommends ReAct → re-run with tools

## Setup

1. `pip install anthropic python-dotenv`
2. Add `ANTHROPIC_API_KEY` to `.env`

## Run

```bash
python "Agentic AI Solution Design Patterns/reflection_pattern/main.py"
```

## Project Structure

```
reflection_pattern/
├── config.py
├── prompts.py       # CoT, ReAct, Reflection prompts
├── tools/            # calendar, venue, catering, document
├── llm_client.py    # Anthropic + reflection parsing
├── controller.py    # Reflection loops
├── agent.py
└── main.py
```

## Reflection Prompts

- **COT_REFLECTION_PROMPT**: Completeness, assumption, logic checks → IMPROVED OUTPUT or VERDICT: SATISFACTORY
- **REACT_REFLECTION_PROMPT**: Outcome analysis, error detection → CORRECTION NEEDED or VERIFIED
- **PATTERN_SWITCH_REFLECTION_PROMPT**: Approach evaluation → SWITCH TO REACT/COT or KEEP
