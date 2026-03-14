# The Learning Module — Explained with Examples

This document illustrates the **learning module** of an autonomous AI agent: how it uses feedback to improve the agent over time.

---

## Learning vs Non-Learning Agents

| Type | Behavior |
|------|----------|
| **Learning agent** | Stores feedback and uses it to improve over time |
| **Non-learning agent** | Carries out the same actions the same way repeatedly; does not store or use feedback for improvement |

The learning module is what makes an agent a **learning agent**.

---

## What Does the Learning Module Do?

The learning module allows the agent to **get better at what it does over time**. Instead of repeating the same behavior, it uses:

- **Feedback** from past experiences
- **What worked and what didn't**
- **Environmental consequences** of actions

To **change behavior**, **improve decisions**, and **adapt to new situations**.

---

## Key Concept: Learning Module Interacts with All Other Modules

```
                    ┌─────────────────────┐
                    │   LEARNING MODULE    │
                    │  (analyzes, refines, │
                    │   improves over time)│
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PERCEPTION    │  │   REASONING     │  │     ACTION      │
│ Refine features │  │ Adjust rules,   │  │ Refine effectors,│
│ object recogn., │  │ heuristics,     │  │ develop new     │
│ filter noise    │  │ goals           │  │ skills          │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Scenario: Warehouse Robot (Locked Door)

*From the transcript — demonstrates learning from feedback.*

### Initial Solution (Before Learning)

**Situation**: Robot encounters locked door to room 303.

**Reasoning**: Problem-solve → text warehouse manager to come and open it.

**Action**: Send notification via API.

**Outcome**: Works, but has drawbacks.

### Feedback Received

| Source | Feedback |
|--------|----------|
| **Human** | Prefers not to run to the door each time |
| **Supervisor** | Task delays are unacceptable |
| **Other robots** | Delays cascade to queued tasks |
| **Internal monitors** | Delivery time exceeds normal allocation |

### Learning Process

1. **Store** the solution and its outcomes
2. **Observe** repeated occurrences (locked door happens again)
3. **Analyze** feedback: text-human solution is slow and disruptive
4. **Identify** better approach: use keypad instead of human
5. **Acquire** new capability: learn keypad code, learn actuator sequence for button presses
6. **Update** reasoning: when door locked → use keypad (not text human)
7. **Update** action: new effector skill — enter code via keypad

### New Solution (After Learning)

**Situation**: Robot encounters locked door.

**Reasoning**: Use keypad (learned from feedback).

**Action**: Enter code via hardware actuators (keypad buttons).

**Outcome**: Faster, no human interruption, no task delays.

---

## Learning Module + Perception

The learning module **continuously analyzes** percepts and their interpretations.

| Activity | Purpose |
|----------|---------|
| Identify patterns | Improve feature extraction |
| Find inconsistencies | Refine object recognition |
| Detect errors | Improve filtering of noise/irrelevant data |
| Iterate | Increase accuracy and reliability of perceptions |

**Goal**: Improve the quality of perceptions passed to the reasoning module.

### Example: Paper Screening Agent

- **Before**: Perception extracts title from first line; sometimes wrong (e.g., "Preprint - Under Peer Review")
- **Feedback**: Manual review shows wrong titles
- **Learning**: Refine extraction — skip boilerplate lines, look for actual title pattern
- **After**: More accurate titles in perceptions

---

## Learning Module + Reasoning

The learning module **observes** planning and decision-making and **evaluates outcomes**.

| Activity | Purpose |
|----------|---------|
| Evaluate outcomes | Which decisions led to success/failure? |
| Adjust decision rules | Refine when to Include/Exclude |
| Adjust heuristics | Improve routing, model selection |
| Propose new goals | More ambitious objectives (depending on agent type) |

### Example: Paper Screening Agent

- **Feedback**: Manual review disagrees with agent on 20% of papers
- **Pattern**: Agent includes "agentic at training time" papers; manual excludes
- **Learning**: Add heuristic — "If agentic loop is only for training/data curation → E2=Y"
- **Update**: Reflection prompt or criterion E2 description refined
- **After**: Fewer false includes on training-time agentic papers

---

## Learning Module + Action

The learning module **analyzes the connection** between actions and environmental consequences.

| Activity | Purpose |
|----------|---------|
| Observe commands + environment changes | What did the action achieve? |
| Refine effector effectiveness | Improve precision, reduce failures |
| Refine effector efficiency | Faster, fewer resources |
| Develop new skills | New capabilities for effectors |

### Example: Paper Screening Agent

- **Feedback**: CSV writes sometimes fail when disk is full
- **Learning**: Add retry logic, check disk space before write
- **New skill**: Fallback to alternative storage if primary fails

---

## How Improvements Are Introduced

The learning module can:

1. **Change or refine predefined rules** — e.g., decision logic, thresholds
2. **Refine logic in AI models** — e.g., fine-tune, adjust prompts, update weights
3. **Use its own models** — dedicated models for managing learning-related information and logic

---

## Summary Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LEARNING MODULE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   INPUTS:                                                                │
│   • Feedback (human, supervisor, other agents, internal monitors)       │
│   • Percepts + interpretations (from Perception)                        │
│   • Planning + decisions + outcomes (from Reasoning)                     │
│   • Actions + environmental consequences (from Action)                   │
│                                                                          │
│   PROCESS:                                                               │
│   • Identify patterns, inconsistencies, errors                           │
│   • Evaluate what worked and what didn't                                 │
│   • Propose refinements                                                 │
│                                                                          │
│   OUTPUTS (to other modules):                                            │
│   • Perception: Refined feature extraction, object recognition, filtering │
│   • Reasoning: Updated rules, heuristics, goals                          │
│   • Action: Refined effectors, new skills                                 │
│                                                                          │
│   OWN MODELS: Manages learning processes, stores experience              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```
