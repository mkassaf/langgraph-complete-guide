# Four-Module Agent — Perception, Reasoning, Action, Learning

This document describes a complete autonomous agent that integrates all four core modules.

---

## The Four Modules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUTONOMOUS AI AGENT                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│   │ PERCEPTION  │────►│ REASONING   │────►│   ACTION    │────►│ Environment│ │
│   │             │     │             │     │             │     │            │ │
│   │ Raw →       │     │ Plan,       │     │ Translate   │     │ (feedback) │ │
│   │ Perceptions │     │ Decide      │     │ Execute     │     │            │ │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └─────┬──────┘ │
│          │                   │                   │                  │        │
│          │                   │                   │                  │        │
│          └───────────────────┴───────────────────┴──────────────────┘       │
│                                      │                                        │
│                                      ▼                                        │
│                            ┌─────────────────┐                               │
│                            │    LEARNING      │                               │
│                            │                  │                               │
│                            │ Store feedback   │                               │
│                            │ Analyze patterns │                               │
│                            │ Refine rules     │                               │
│                            └────────┬────────┘                               │
│                                     │                                         │
│                    ┌────────────────┼────────────────┐                       │
│                    ▼                ▼                ▼                       │
│              Perception        Reasoning         Action                       │
│              (refine)          (adjust)          (improve)                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Paper Screening Agent

| Step | Module | Input | Output |
|------|--------|-------|--------|
| 1 | **Perception** | PDF file (raw) | `{title, abstract, full_text, metadata}` |
| 2 | **Reasoning** | Perceptions | `{include: bool, reason: str, criterion_results}` |
| 3 | **Action** | Decision + perceptions | Write to CSV, monitor success |
| 4 | **Learning** | Outcome + optional manual feedback | Store, analyze, refine rules |

---

## Module Responsibilities

### 1. Perception Module
- **Collect**: PDF bytes, raw text, metadata
- **Process**: Clean encoding, truncate
- **Interpret**: Extract title, abstract, spatial map
- **Output**: Structured perceptions for reasoning

### 2. Reasoning Module
- **Plan**: Evaluate I1, I2, E1, E2, E3, E7
- **Decide**: Apply rules (I1=Y, I2=Y, all E=N → Include)
- **Output**: Include/Exclude + reason

### 3. Action Module
- **Translate**: Decision → command for effector
- **Execute**: Write row to CSV (file system effector)
- **Monitor**: Success, latency

### 4. Learning Module
- **Store**: Outcomes, manual feedback
- **Analyze**: Patterns (e.g., manual disagrees on training-time agentic)
- **Refine**: Update rules for Perception, Reasoning, Action

---

## Running the Example

```bash
# Simulated reasoning (no API keys)
python examples/four_modules_agent.py

# Real LLM (requires DEEPSEEK_API_KEY, OPENAI_API_KEY)
USE_REAL_LLM=1 python examples/four_modules_agent.py
```

Output is written to `output/examples/four_modules_results.csv`.

---

## Relation to Individual Module Examples

| Example | Focus |
|---------|-------|
| `perception_module_demo.py` | Perception only |
| `reasoning_module_demo.py` | Reasoning only |
| `action_module_demo.py` | Action only |
| `learning_module_demo.py` | Learning only |
| **`four_modules_agent.py`** | **All four modules together** |
