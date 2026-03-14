# The Reasoning Module — Explained with Examples

This document illustrates the **reasoning module** of an autonomous AI agent using the concepts from the course and concrete examples.

---

## What is the Reasoning Module?

The reasoning module receives **perceptions** from the perception module and decides **what action(s) to take**. It uses:

- **Planning** — creating a sequence of steps
- **Decision-making logic** — predefined rules and/or model (LLM) logic
- **Problem-solving** — handling unexpected situations
- **Knowledge management** — organizing and using AI models and data
- **Inference engine** — executing the logic

```
Perceptions → Plan → Decide → (Unexpected?) → Problem-solve → Actions
                    ↓
              Knowledge (models, rules)
                    ↓
              Perception (refine sensing?)
```

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Planning** | Creating a sequence of steps to achieve a goal (simple or complex) |
| **Predefined rules** | Logic for situations the agent was designed to handle |
| **Model logic** | LLM or other AI model used for reasoning |
| **Problem-solving** | Ad hoc solutions when the agent hits an unexpected situation |
| **Feedback** | Information from the environment (e.g., action failed) that triggers new reasoning |
| **Knowledge management** | Organizing models and data the agent uses |
| **Inference engine** | The component that runs the reasoning logic |
| **Perception refinement** | Reasoning can ask the perception module to improve what it senses or tags |

---

## Example 1: Warehouse Robot (from the Transcript)

*Robot must deliver a box from the warehouse to room 303.*

### Step 1: Planning

The reasoning module receives perceptions (box location, room 303 location, map) and creates a plan:

```
Plan:
  1. Pick up box
  2. Navigate to corridor
  3. Walk toward room 303
  4. Enter door of room 303
  5. Place box
```

### Step 2: Expected Obstacle — Predefined Logic

While walking, the robot encounters a **human blocking the path** — a situation it was designed for.

```
Perception: Human detected at (x, y), blocking path
Decision logic (predefined): IF human_blocks_path THEN navigate_around
Action: Execute detour around human
```

No ad hoc problem-solving needed; predefined rules handle it.

### Step 3: Unexpected Problem — Problem-Solving

The robot reaches the door. Usually it's unlocked. This time it's **locked**.

```
Perception: At door of room 303
Action: Attempt to open door (turn knob)
Feedback: Action FAILED — door is locked

Reasoning (problem-solving):
  - Unexpected: door locked
  - Available knowledge: warehouse manager can unlock
  - Solution: Send text to warehouse manager requesting access
  - New plan: Wait for manager → door opens → proceed
```

The reasoning module uses feedback (failure) and available knowledge to create an **ad hoc** solution.

### Step 4: Perception Refinement (Feedback Loop)

Later, the reasoning module realizes: *"If I had known the door was locked before trying, I could have texted the manager immediately."*

```
Reasoning → Perception: "Tag the door keypad light (locked/unlocked) as relevant"
Perception: Now includes "door_locked: true/false" in future perceptions
Reasoning: Next time, check door_locked first; if true, skip open attempt and text manager
```

The reasoning module instructs the perception module to **improve what it senses** so future decisions are better.

---

## Example 2: Paper Screening Agent (Project Context)

*Agent must decide whether to Include or Exclude each paper.*

### Step 1: Planning

The reasoning module receives perceptions (title, abstract, full text) and creates a plan:

```
Plan:
  1. Evaluate I1 (LLM-based agentic?)
  2. Evaluate I2 (Energy relevance?)
  3. Evaluate E1, E2, E3, E7 (Exclusion criteria)
  4. Apply decision logic → Include or Exclude
  5. If Include: generate summary
```

### Step 2: Decision-Making Logic (Rules + Model)

| Criterion | Type | Logic |
|-----------|------|-------|
| I1, I2, E1, E2, E3, E7 | **Model (LLM)** | DeepSeek evaluates each criterion from paper text |
| Final decision | **Rules** | `INCLUDE = (I1=Y AND I2=Y) AND (E1=N AND E2=N AND E3=N AND E7=N)` |
| Reflection | **Model (LLM)** | GPT-4o-mini validates criterion outputs |

Predefined rules define the decision formula; the LLM provides the criterion evaluations.

### Step 3: Unexpected Problem — Edge Cases

**Expected**: Paper clearly agentic, clearly has cost discussion → straightforward Include/Exclude.

**Unexpected**: Paper is borderline — e.g., "agentic loop for training" vs "agentic at inference."

```
Perception: Paper discusses "agentic framework" for data curation
Model (I1): "Y" — it mentions agentic
Model (E2): "N" — no exclusion
Rule: → INCLUDE

Reflection (problem-solving): "Wait — is this agentic at inference time or only for training?"
Reflection overrides: Suggests E2=Y (not agentic in deployed sense)
Revised decision: EXCLUDE
```

The reflection step acts as **problem-solving** for ambiguous cases the main model didn't handle well.

### Step 4: Knowledge Management

The reasoning module uses multiple "models":

| Model | Role |
|-------|------|
| Criterion agents (I1, I2, E1, E2, E3, E7) | Evaluate each criterion |
| Reflection model | Validate and correct outputs |
| Decision rules (config) | Combine criterion results |
| Knowledge representation | Criteria definitions, expected outputs |

The **inference engine** (LangChain + run loop) orchestrates calls to these models and applies the rules.

### Step 5: Perception Refinement (Hypothetical)

If the reasoning module found that **missing metadata** (e.g., arxiv_id) caused wrong routing:

```
Reasoning → Perception: "Always extract and tag arxiv_id from filename"
Perception: Now includes arxiv_id in every paper's perceptions
Reasoning: Can now match papers to manual review by arxiv_id
```

---

## Example 3: Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        REASONING MODULE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   PERCEPTIONS (from Perception Module)                                   │
│            │                                                              │
│            ▼                                                              │
│   ┌────────────────┐                                                     │
│   │    PLANNING    │  "What sequence of steps do I need?"                │
│   └────────┬───────┘                                                     │
│            │                                                              │
│            ▼                                                              │
│   ┌────────────────┐     ┌─────────────────────┐                        │
│   │ DECISION LOGIC  │────▶│ Predefined rules    │                        │
│   │                 │     │ Model (LLM) logic   │                        │
│   └────────┬───────┘     └─────────────────────┘                        │
│            │                                                              │
│            ▼                                                              │
│   ┌────────────────┐                                                     │
│   │    ACTIONS      │  Execute (or send to Action Module)                │
│   └────────┬───────┘                                                     │
│            │                                                              │
│            ▼                                                              │
│   ┌────────────────┐                                                     │
│   │    FEEDBACK     │  Success? Failure? New info?                      │
│   └────────┬───────┘                                                     │
│            │                                                              │
│     ┌──────┴──────┐                                                      │
│     │ Unexpected? │                                                      │
│     └──────┬──────┘                                                      │
│       Yes  │  No                                                         │
│            ▼                                                             │
│   ┌────────────────┐                                                     │
│   │ PROBLEM-SOLVE   │  Ad hoc solution using knowledge + analysis         │
│   └────────┬───────┘                                                     │
│            │                                                              │
│            ▼                                                              │
│   ┌────────────────┐                                                     │
│   │ REFINE         │  Instruct Perception to improve sensing?            │
│   │ PERCEPTION?    │  (e.g., tag door lock indicator)                    │
│   └────────────────┘                                                     │
│                                                                          │
│   KNOWLEDGE: Models (LLM, vision), rules, criteria definitions            │
│   INFERENCE ENGINE: Runs the logic, calls models, applies rules           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Summary

| Function | Warehouse Robot | Paper Screening Agent |
|----------|-----------------|------------------------|
| **Planning** | Path to room 303, steps to door | Evaluate I1→I2→E1→E2→E3→E7, then decide |
| **Predefined logic** | Navigate around human | Decision rule: I1=Y, I2=Y, all E=N → Include |
| **Model logic** | (optional) LLM for navigation | DeepSeek for criteria, GPT-4o for reflection |
| **Problem-solving** | Door locked → text manager | Borderline paper → reflection overrides |
| **Feedback** | "Open door" failed | Criterion outputs inconsistent |
| **Perception refinement** | Tag door lock indicator | Ensure arxiv_id in perceptions |
