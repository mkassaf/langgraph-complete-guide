# Agentic AI Architecture

Examples demonstrating the four core modules of autonomous AI agents (Perception, Reasoning, Action, Learning) and four agent types (Simple Reflex, Model-Based Reflex, Goal-Based, Utility-Based).

---

## Core Modules

| Module | Role |
|--------|------|
| **Perception** | Collect raw data → process → form perceptions for reasoning |
| **Reasoning** | Plan → decide (rules, model, or utility) → output action |
| **Action** | Translate decision → execute via effectors → monitor |
| **Learning** | Store feedback → analyze → refine rules (Goal-Based, Utility-Based only) |

---

## Module Examples

### 1. Perception Module

| File | Description |
|------|-------------|
| `perception_module_example.md` | Concepts: percepts vs perceptions, physical vs digital sensors, spatial mapping |
| `perception_module_demo.py` | Runnable: PDF loading for paper screening agent |

```bash
python examples/"Agentic AI Architecture"/perception_module_demo.py
```

### 2. Reasoning Module

| File | Description |
|------|-------------|
| `reasoning_module_example.md` | Concepts: planning, predefined rules, problem-solving, perception refinement |
| `reasoning_module_demo.py` | Runnable: warehouse robot + paper screening (real LLM calls) |

```bash
python examples/"Agentic AI Architecture"/reasoning_module_demo.py
```

Requires: `DEEPSEEK_API_KEY`, `OPENAI_API_KEY` in `.env`

### 3. Action Module

| File | Description |
|------|-------------|
| `action_module_example.md` | Concepts: effectors, granularity, effector management, monitoring |
| `action_module_demo.py` | Runnable: fine-grained vs coarse-grained actions, CSV + API effectors |

```bash
python examples/"Agentic AI Architecture"/action_module_demo.py
```

### 4. Learning Module

| File | Description |
|------|-------------|
| `learning_module_example.md` | Concepts: feedback, learning from experience, refining other modules |
| `learning_module_demo.py` | Runnable: warehouse robot (locked door), paper screening feedback |

```bash
python examples/"Agentic AI Architecture"/learning_module_demo.py
```

---

## Integrated Examples

### 5. Four Modules Together

| File | Description |
|------|-------------|
| `four_modules_example.md` | How all four modules connect in one agent |
| `four_modules_agent.py` | Full pipeline: Perception → Reasoning → Action → Learning |

```bash
# Simulated reasoning (no API keys)
python examples/"Agentic AI Architecture"/four_modules_agent.py

# Real LLM
USE_REAL_LLM=1 python examples/"Agentic AI Architecture"/four_modules_agent.py
```

### 6. Warehouse Agent Types Simulation

| File | Description |
|------|-------------|
| `warehouse_agents_simulation.py` | All four agent types: Simple Reflex, Model-Based Reflex, Goal-Based, Utility-Based |

Scenario: Room 303 has locked door + human obstacle. Each agent type handles it differently.

```bash
python examples/"Agentic AI Architecture"/warehouse_agents_simulation.py
```

| Agent Type | Perception | Reasoning | Action | Learning |
|------------|------------|-----------|--------|----------|
| **Simple Reflex** | Raw percepts only | Lookup rules | Single action | None |
| **Model-Based Reflex** | Percepts + internal model | Model + rules | Simple actions | None |
| **Goal-Based** | Current vs goal state | Plan multi-step | Execute sequence | Yes |
| **Utility-Based** | Evaluate utility scores | Maximize utility | Coordinate complex | Yes |

---

## File Overview

```
Agentic AI Architecture/
├── README.md                      # This file
├── perception_module_example.md   # Perception concepts
├── perception_module_demo.py      # Perception demo
├── reasoning_module_example.md    # Reasoning concepts
├── reasoning_module_demo.py       # Reasoning demo (LLM)
├── action_module_example.md       # Action concepts
├── action_module_demo.py          # Action demo
├── learning_module_example.md     # Learning concepts
├── learning_module_demo.py        # Learning demo
├── four_modules_example.md        # Four modules overview
├── four_modules_agent.py          # Full agent pipeline
└── warehouse_agents_simulation.py # Four agent types
```

---

## Prerequisites

- Python 3.10+
- For LLM demos: `langchain-openai`, `python-dotenv`, API keys in `.env`
- For perception/four_modules: PDFs in `output/pdfs/`
