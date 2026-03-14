# Chain of Thought — Event Planning Demo

Demonstrates the **Chain of Thought** design pattern using the Anthropic Claude API, applied to an event planning scenario.

## Scenario

An AI agent plans a half-day team offsite meeting for 15 people next month. The meeting must be in-person, engaging, and include catering. The demo shows the clear difference between LLM responses **with** and **without** Chain of Thought prompting.

## Setup

1. Install dependencies:
   ```bash
   pip install anthropic python-dotenv
   ```

2. Add `ANTHROPIC_API_KEY` to your `.env` file (project root):
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
   Get a key at: https://console.anthropic.com/

## Run

From project root:
```bash
python "Agentic AI Solution Design Patterns/chain_of_thought/main.py"
```

Or from within the chain_of_thought folder:
```bash
cd "Agentic AI Solution Design Patterns/chain_of_thought"
python main.py
```

## Project Structure

```
chain_of_thought/
├── config.py       # API config and constants
├── prompts.py      # System prompts (no CoT vs CoT)
├── llm_client.py   # Anthropic API wrapper
├── agent.py        # Controller + EventPlanningAgent
├── comparator.py   # Runs both modes, compares results
├── main.py         # Entry point
└── README.md
```

## Design Pattern

- **Controller**: Intermediary between LLM and outside world; selects system prompt based on task complexity
- **LLM**: Reasoning module component; generates responses via Anthropic API
- **Chain of Thought**: Structured reasoning prompt (THOUGHT 1–4) forces step-by-step analysis

---

# Designing System Prompts for the Chain of Thought Pattern

---

## Core Principle

The System Prompt in Chain of Thought is **instructions for the LLM that define HOW to think** — not WHAT to think.

---

## Basic System Prompt Structure

```
┌─────────────────────────────────────┐
│           System Prompt             │
│                                     │
│  1. Role Definition (Who)           │
│  2. Thinking Instructions (How)     │
│  3. Steps Structure                 │
│  4. Output Format                   │
└─────────────────────────────────────┘
```

---

## The Four Components in Detail

### 1. Role Definition
```
"You are an expert [domain] assistant 
 that reasons carefully before answering."
```

### 2. Thinking Instructions
```
"When given a task, you MUST:
 - Break it into steps
 - Show your reasoning at each step
 - Do NOT jump to conclusions"
```

### 3. Steps Structure
```
"STEP 1 - ANALYZE:    ← What to do in this step
 ...your analysis...

 STEP 2 - CONSIDER:   ← What to do in this step
 ...your considerations...

 STEP 3 - CONCLUDE:   ← What to do in this step
 ...your conclusion..."
```

### 4. Output Format
```
"Format each step with its label.
 Show ALL reasoning before final answer.
 End with: FINAL ANSWER: ..."
```

---

## System Prompt Types by Task

### Type 1: Analytical Tasks (e.g., meeting planning)
```python
ANALYTICAL_COT_PROMPT = """
You are a careful planning assistant.

For every request, follow these steps:

THOUGHT 1 - ANALYZE:
- What are the explicit requirements?
- What is vague or ambiguous?
- What information is missing?

THOUGHT 2 - RESEARCH PLAN:
- What do I need to find out?
- What are the constraints?
- What dependencies exist?

THOUGHT 3 - EVALUATE OPTIONS:
- What are the possible approaches?
- Pros and cons of each?
- What could go wrong?

THOUGHT 4 - RECOMMEND:
- Best option based on analysis
- Clear reasoning for choice
- Assumptions made

Show ALL thoughts before giving final answer.
"""
```

---

### Type 2: Mathematical/Logical Tasks
```python
MATH_COT_PROMPT = """
You are a precise reasoning assistant.

Solve problems using this exact format:

GIVEN:
List all known information

STEP 1: [action taken]
[show calculation or logic]

STEP 2: [action taken]  
[show calculation or logic]

...continue until solved...

ANSWER: [final result]
VERIFY: [check your answer makes sense]
"""
```

---

### Type 3: Diagnostic Tasks (e.g., debugging)
```python
DEBUG_COT_PROMPT = """
You are an expert debugger.

When analyzing a problem:

OBSERVE:
What symptoms or errors are present?

HYPOTHESIZE:
What could be causing this? List ALL possibilities.

TEST:
How would you verify each hypothesis?
Start with most likely cause.

DIAGNOSE:
Based on evidence, what is the root cause?

FIX:
What is the solution and why does it work?
"""
```

---

### Type 4: Resource-Constrained Tasks (lightweight)
```python
LIGHTWEIGHT_COT_PROMPT = """
You are a helpful assistant.

Think briefly before answering:
- What is really being asked?
- What's the key consideration?
- What's the best response?

Then give your answer.
"""
```

---

## Comparison: Simple Prompt vs Chain of Thought

```
Simple Prompt:
─────────────
"You are a helpful assistant.
 Answer the user's question."

         ↓ LLM jumps to answer directly

Chain of Thought:
─────────────────
"You are a helpful assistant.
 
 Before answering, you MUST:
 
 STEP 1 - UNDERSTAND:
 What exactly is being asked?
 What assumptions might I make?
 
 STEP 2 - THINK:
 What factors should I consider?
 What are the tradeoffs?
 
 STEP 3 - ANSWER:
 Based on steps 1 and 2, my answer is...
 
 Show each step explicitly."

         ↓ LLM thinks in an organized way
```

---

## Rules for Effective System Prompt Design

```
✅ Do:                         ❌ Don't:
─────────────                  ────────────────
Be specific in steps          Don't be vague
Use clear labels               Don't leave structure open
Define output format           Don't assume the LLM knows
Ask to show reasoning          Don't ask for result only
Use appropriate step count     Don't overcomplicate with extra steps
```

---

## When to Use More or Fewer Steps?

| Step Count | When |
|------------|------|
| **2 steps** | Relatively simple tasks |
| **3–4 steps** | Medium-complexity tasks — most common |
| **5+ steps** | Very complex tasks needing deep analysis |

---

## Full Practical Example

```python
# For an agent that plans meetings
MEETING_PLANNER_COT = """
You are an expert meeting planner.

When asked to plan any meeting or event, 
you MUST think through it in this order:

THOUGHT 1 - CLARIFY REQUIREMENTS:
- List every explicit requirement from the request
- Identify vague terms and how you interpret them
- Note what critical information is missing

THOUGHT 2 - ASSESS CONSTRAINTS:
- What are the time/date constraints?
- What are the budget constraints (if any)?
- What are the attendance/size constraints?
- What logistics need coordination?

THOUGHT 3 - GENERATE OPTIONS:
- List at least 2-3 viable approaches
- For each option note: pros, cons, risks

THOUGHT 4 - RECOMMEND:
- Choose best option with clear reasoning
- List your assumptions explicitly
- Identify next steps needed

IMPORTANT: 
- Never skip a THOUGHT
- Always show reasoning before conclusion
- Flag anything that needs human confirmation
"""
```

---

## Summary

> Designing a System Prompt for Chain of Thought means **turning implicit thinking into an explicit, structured process** — the clearer and more specific the steps, the better and more reliable the LLM's reasoning.
