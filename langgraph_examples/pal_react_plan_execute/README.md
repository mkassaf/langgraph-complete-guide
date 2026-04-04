# PAL vs ReAct vs Plan-and-Execute — Three Agent Patterns in LangGraph

This folder contains three self-contained LangGraph examples that each solve the **same class of problems** using a fundamentally different strategy. Understanding the differences is key to choosing the right pattern for your own agents.

---

## The Core Idea Behind All Three

All three patterns are answers to the same question:

> **"How should an AI agent combine language understanding with reliable computation?"**

LLMs are great at language but unreliable at arithmetic, precise reasoning over many steps, and long-horizon planning. Each pattern handles this limitation differently.

---

## Pattern 1 — PAL: Program-Aided Language Models

**File:** `example_pal.py`

### What is PAL?

PAL was introduced in the 2022 paper *"PAL: Program-aided Language Models"* (Gao et al.). The key insight is simple:

> **Do not ask the LLM to calculate — ask it to WRITE CODE that calculates.**

Instead of chain-of-thought reasoning ("Let me think step by step..."), the LLM generates a Python program. That program is then **executed by a Python interpreter** and the output is used as the answer.

### Why does this help?

| Problem | Chain-of-Thought LLM | PAL |
|---------|----------------------|-----|
| `23 × 47 = ?` | May guess 1,081 (wrong) | Writes `print(23 * 47)` → 1081 ✓ |
| Complex word problem | May lose track of variables | Variables are in code — never forgotten |
| Multi-step arithmetic | Each step adds error risk | Python is deterministic |

### The LangGraph Graph

```
START → [generate_code] → [execute_code] → [format_answer] → END
```

Each node has a single, clear responsibility:

| Node | Input | Does | Output |
|------|-------|------|--------|
| `generate_code` | question (text) | LLM writes Python program | Python code (string) |
| `execute_code` | Python code | `exec()` in sandbox | printed output (string) |
| `format_answer` | code + output | LLM writes natural-language sentence | final_answer (string) |

### State

```python
class PALState(TypedDict):
    question:       str   # "A train travels at 80 km/h for 2.5 hours..."
    generated_code: str   # "speed1 = 80\ntime1 = 2.5\n..."
    code_output:    str   # "200.0"
    final_answer:   str   # "The total distance is 200 km."
```

### Concrete trace

```
Question: "A store sells apples for $1.25. Buy 17, pay $25. Change?"

── generate_code ──────────────────────────────────────
price_per_apple = 1.25
apples = 17
paid = 25
total_cost = price_per_apple * apples
change = paid - total_cost
print(change)

── execute_code ───────────────────────────────────────
3.75

── format_answer ──────────────────────────────────────
"You would receive $3.75 in change."
```

### When to use PAL
- The problem is primarily **computational** (math, counting, logic puzzles).
- You can express the solution as a **short Python script**.
- You want **deterministic, verifiable** answers.
- The problem does NOT require querying external tools or dynamic branching.

### Limitations of PAL
- Cannot search the web, call APIs, or retrieve facts.
- Only works when the answer can be reached via code.
- One shot — if the code is wrong, there is no retry loop.

---

## Pattern 2 — ReAct: Reasoning + Acting

**File:** `example_react.py`

### What is ReAct?

ReAct was introduced in the 2022 paper *"ReAct: Synergizing Reasoning and Acting in Language Models"* (Yao et al.). The key insight:

> **Interleave THINKING (reasoning) with DOING (tool calls) in a dynamic loop.**

The original paper used explicit text labels: `Thought:`, `Action:`, `Observation:`. Modern LLMs with function-calling do this implicitly — but the structure is the same.

### The ReAct Loop

```
User Question
    ↓
  [Thought]  → "I need to find the population of France first"
  [Action]   → call lookup_fact("population of france")
  [Observation] → "France has ~68 million people"
    ↓
  [Thought]  → "Now I need Germany's population"
  [Action]   → call lookup_fact("population of germany")
  [Observation] → "Germany has ~84 million people"
    ↓
  [Thought]  → "Now I can compare them"
  [Action]   → call calculator("84000000 - 68000000")
  [Observation] → "16000000"
    ↓
  [Final Answer] → "Germany has 16 million more people than France"
```

There is **no plan** written at the start. The agent decides its next tool call **dynamically** based on what it has already observed.

### The LangGraph Graph

```
START → [agent] ─── (has tool_calls?) ──→ [tools] ──┐
                └──── (no tool_calls) ──→ END        │
                 ↑                                    │
                 └────────────────────────────────────┘
```

This is the classic **agent ↔ tools loop**. The `tools_condition` function (provided by LangGraph) routes:
- `tool_calls` present → go to `tools` node → come back to `agent`
- No `tool_calls` → go to `END` (final answer reached)

### State

ReAct uses `MessagesState` (built into LangGraph) — a list of messages:

```
[HumanMessage("What is ...")]           ← user question
[AIMessage(tool_calls=[...])]           ← agent's action
[ToolMessage("The result is ...")]      ← tool's observation
[AIMessage(tool_calls=[...])]           ← agent's next action
[ToolMessage("...")]                    ← another observation
[AIMessage("The final answer is...")]   ← final answer (no tool_calls)
```

### When to use ReAct
- The task requires **multiple different tools** used in an **unpredictable order**.
- Each next step **depends on the result of the previous step** (you cannot plan upfront).
- You need **dynamic, adaptive behaviour** (e.g., if a tool fails, try another).
- Good for: web research, customer support, question answering, agentic assistants.

### Limitations of ReAct
- No global view of the task — can get "lost" on long multi-step problems.
- May make redundant tool calls (no plan to refer back to).
- Hard to debug: the order of tool calls emerges emergently at runtime.

---

## Pattern 3 — Plan-and-Execute

**File:** `example_plan_execute.py`

### What is Plan-and-Execute?

Plan-and-Execute (also called "Plan-then-Solve" or "Task Decomposition" in some literature) separates planning and execution into two distinct, explicit phases:

> **Phase 1 — PLAN:** A "planner" LLM produces a complete numbered list of steps BEFORE any tools are called.
> **Phase 2 — EXECUTE:** An "executor" works through the steps one by one, calling tools and collecting results.

This mirrors how humans tackle complex projects: write the plan first, then execute it.

### The LangGraph Graph

```
START → [planner] → [executor] ─── (more steps?) ──→ [executor] (loop)
                                └── (all done?) ───→ [finalizer] → END
```

The router (`route_after_executor`) checks `step_index >= len(plan)`:
- If more steps remain → loop back to `executor`
- If all steps done → go to `finalizer`

### State

```python
class PlanExecuteState(TypedDict):
    task:         str        # "Compare France and Germany by GDP per capita"
    plan:         List[str]  # ["1. Look up France GDP", "2. Look up France population", ...]
    step_index:   int        # 0, 1, 2, ... (which step we're currently executing)
    step_results: List[str]  # accumulated results from each step
    final_answer: str        # synthesised answer after all steps
```

### Concrete trace

```
Task: "Compare France and Germany by GDP per capita"

── Planner ──────────────────────────────────────────────
  1. Look up France GDP using lookup_statistic('gdp of france')
  2. Look up France population using lookup_statistic('population of france')
  3. Look up Germany GDP using lookup_statistic('gdp of germany')
  4. Look up Germany population using lookup_statistic('population of germany')
  5. Calculate France GDP per capita: calculate('3050000000000 / 68000000')
  6. Calculate Germany GDP per capita: calculate('4460000000000 / 84000000')
  7. Compare the two values

── Executor: step 1 ─────────────────────────────────────
  [Tool: lookup_statistic] → gdp of france = 3,050,000,000,000

── Executor: step 2 ─────────────────────────────────────
  [Tool: lookup_statistic] → population of france = 68,000,000

  ... (steps 3-7) ...

── Finalizer ────────────────────────────────────────────
  "Germany has a higher GDP per capita ($53,095) compared to France
   ($44,853). Germany's per-capita GDP is approximately 18.4% higher."
```

### When to use Plan-and-Execute
- The task is **complex and multi-step** but the steps can be anticipated upfront.
- You want the agent to have a **global view** before it starts acting.
- Steps are **largely independent** — each can execute without needing to re-reason from scratch.
- You need **transparency**: a human or supervisor can review the plan before execution starts.
- Good for: research reports, data pipelines, structured workflows.

### Limitations of Plan-and-Execute
- If the plan is wrong (bad planner), all subsequent steps are wasted.
- Less adaptive than ReAct: the plan may not handle unexpected tool results without a replanner.
- Overhead: requires an extra LLM call just for planning.

---

## Side-by-Side Comparison

| Property | PAL | ReAct | Plan-and-Execute |
|----------|-----|-------|-----------------|
| **Core idea** | LLM writes code; Python runs it | LLM thinks and acts in a loop | Plan first; execute step by step |
| **Number of LLM calls** | 2–3 (fixed) | Dynamic (1 per loop iteration) | `2 + N` (plan + N executor calls + finalize) |
| **Tool usage** | None (Python is the "tool") | Any tools, any order, dynamic | Fixed tools; order determined by plan |
| **Global task view** | Yes — the whole program at once | No — greedy, one step at a time | Yes — full plan exists before execution |
| **Adaptability** | None — single shot | High — reacts to each observation | Medium — can add replanner node |
| **Best for** | Math / logic / computation | Dynamic research, Q&A | Multi-step structured workflows |
| **Debuggability** | Easy — just read the code | Hard — emergent call order | Easy — plan is inspectable upfront |
| **Risk of getting stuck** | Code errors (one-shot) | Infinite loops (needs max iterations) | Bad initial plan |

---

## Visual Architecture Diagrams

### PAL

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  START   │───▶│generate_code │───▶│ execute_code │───▶│format_answer │───▶ END
└──────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                 LLM writes           Python exec()       LLM formats
                 Python code          captures stdout     the result
```

### ReAct

```
┌───────┐    ┌───────┐    tool_calls?
│ START │───▶│ agent │──────────────YES──────▶ ┌───────┐
└───────┘    └───────┘                          │ tools │
                 ▲                              └───────┘
                 │◀──────────────────────────────────┘
                 │
                 └──NO (content only)──▶ END
```

### Plan-and-Execute

```
┌───────┐    ┌─────────┐    ┌──────────┐    more steps?
│ START │───▶│ planner │───▶│ executor │────────YES──────┐
└───────┘    └─────────┘    └──────────┘                 │
                                  ▲                       │
                                  └───────────────────────┘
                                  │
                                  └──all done──▶ ┌───────────┐
                                                  │ finalizer │───▶ END
                                                  └───────────┘
```

---

## How They Relate: A Mental Model

Think of planning a trip:

| Analogy | Pattern |
|---------|---------|
| You ask a calculator to figure out the fuel cost for each leg | **PAL** — offload computation, don't do it in your head |
| You navigate turn-by-turn, deciding each turn based on what you see | **ReAct** — dynamic, reactive, no upfront route |
| You plan the full itinerary the night before, then follow it | **Plan-and-Execute** — global plan, then systematic execution |

---

## Running the Examples

Prerequisites: set `OPENAI_API_KEY` in a `.env` file at the project root.

```bash
# PAL — Program-Aided Language Models
python langgraph_examples/pal_react_plan_execute/example_pal.py

# ReAct — Reasoning + Acting
python langgraph_examples/pal_react_plan_execute/example_react.py

# Plan-and-Execute
python langgraph_examples/pal_react_plan_execute/example_plan_execute.py
```

No additional packages are needed beyond the project's `requirements.txt`.

---

## Key LangGraph Concepts Demonstrated

| Concept | Where Used |
|---------|-----------|
| `TypedDict` state | All three — custom state shapes |
| Linear graph (`add_edge` only) | PAL — no branching, no loops |
| `tools_condition` + agent loop | ReAct — conditional routing to tools |
| `MessagesState` | ReAct — append-only message list |
| `bind_tools()` | ReAct, Plan-and-Execute executor — LLM gets tool schemas |
| `ToolNode` | ReAct — auto-dispatches tool_calls |
| Conditional edges (`add_conditional_edges`) | Plan-and-Execute — loop vs finalize |
| Multi-node routing | Plan-and-Execute — planner → executor → finalizer |
| Structured output parsing | Plan-and-Execute — plan parsed from LLM text |
