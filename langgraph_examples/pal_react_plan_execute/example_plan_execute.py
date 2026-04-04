# file: langgraph_examples/pal_react_plan_execute/example_plan_execute.py
"""
Plan-and-Execute in LangGraph
──────────────────────────────
Plan-and-Execute separates PLANNING from DOING into two distinct phases:

Phase 1 — PLAN:  A dedicated "planner" LLM call looks at the overall goal
                  and writes a numbered list of concrete steps to accomplish it.

Phase 2 — EXECUTE: A dedicated "executor" works through the plan one step at a time,
                    calling tools and recording results.  When all steps are done,
                    a "finalizer" synthesises the collected results into a final answer.

  Optional Phase 3 — REPLAN: After execution, if the results are incomplete or
                    contradictory, the planner can revise the remaining steps.
                    (Included here as a conditional route.)

Why Plan-and-Execute instead of ReAct?
  ReAct            — greedy, one tool call at a time, no global view of the task.
                     Works well when the next step depends heavily on the previous result.
  Plan-and-Execute — creates a birds-eye plan first, avoids redundant tool calls,
                     better suited for complex multi-step research tasks.
  PAL              — code-centric, single-shot, best for pure computation problems.

Graph:
  START → [planner] → [executor] → (replanner or finalizer) → END
                           ↑               |
                           └── loop back ──┘  (if steps remain)

State:
  task          — the overall goal/question
  plan          — ordered list of steps (strings) from the planner
  step_index    — which step we're executing next
  step_results  — accumulated results from each executed step
  final_answer  — synthesised answer after all steps are complete
"""

from typing import TypedDict, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ─── State ─────────────────────────────────────────────────────────────────────
class PlanExecuteState(TypedDict):
    task:         str
    plan:         List[str]   # ["Step 1: ...", "Step 2: ...", ...]
    step_index:   int         # which step we're on (0-based)
    step_results: List[str]   # results collected so far (one entry per executed step)
    final_answer: str


# ─── Tools (same simple set as the ReAct example) ──────────────────────────────
FACTS_DB = {
    "population of france":   68_000_000,
    "population of germany":  84_000_000,
    "population of japan":   125_000_000,
    "gdp of france":         3_050_000_000_000,   # USD
    "gdp of germany":        4_460_000_000_000,   # USD
    "gdp of japan":          4_230_000_000_000,   # USD
    "area of france":          643_801,            # km²
    "area of germany":         357_114,            # km²
    "area of japan":           377_975,            # km²
}

@tool
def lookup_statistic(key: str) -> str:
    """
    Return a numeric statistic for a country.
    Supported keys (lowercase): 'population of <country>', 'gdp of <country>',
    'area of <country>'.
    Example: 'population of france', 'gdp of germany'.
    """
    val = FACTS_DB.get(key.lower().strip())
    if val is None:
        available = ", ".join(FACTS_DB.keys())
        return f"Not found. Available keys: {available}"
    return f"{key} = {val:,}"


@tool
def calculate(expression: str) -> str:
    """
    Evaluate a Python arithmetic expression and return the result.
    Input must be a valid expression, e.g. '84000000 - 68000000' or '4460/3050'.
    Use this for all arithmetic after you have looked up the raw numbers.
    """
    safe_globals = {"__builtins__": {}, "round": round, "abs": abs}
    try:
        result = eval(expression, safe_globals)
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"


@tool
def compare(a: float, b: float, label_a: str, label_b: str) -> str:
    """
    Compare two numbers and return which is larger and by how much.
    Provide the numeric values (a, b) and their human-readable labels (label_a, label_b).
    Returns a formatted comparison statement.
    """
    if a > b:
        diff = a - b
        pct  = (diff / b) * 100
        return f"{label_a} ({a:,.0f}) is larger than {label_b} ({b:,.0f}) by {diff:,.0f} ({pct:.1f}%)."
    elif b > a:
        diff = b - a
        pct  = (diff / a) * 100
        return f"{label_b} ({b:,.0f}) is larger than {label_a} ({a:,.0f}) by {diff:,.0f} ({pct:.1f}%)."
    else:
        return f"{label_a} and {label_b} are equal ({a:,.0f})."


TOOLS_DESCRIPTIONS = """
Available tools:
- lookup_statistic(key: str) — get population / GDP / area for a country
  Keys: 'population of <country>', 'gdp of <country>', 'area of <country>'
  Countries: france, germany, japan
- calculate(expression: str) — evaluate arithmetic, e.g. '84000000 - 68000000'
- compare(a, b, label_a, label_b) — compare two numbers and report the difference
"""

# ─── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ─── Node 1: planner ───────────────────────────────────────────────────────────
# The planner sees the full task and returns a numbered list of self-contained steps.
# Each step should be executable independently.
PLANNER_PROMPT = """\
You are a careful planner. Break the following task into a numbered list of
concrete, self-contained steps.

{tools}

Rules:
- Each step should do ONE thing (one tool call or one reasoning operation).
- Be explicit: name the tool and the inputs you'll use.
- Do NOT perform any steps yourself — just write the plan.
- Return ONLY the numbered list, nothing else.

Task: {task}
"""

def planner_node(state: PlanExecuteState) -> dict:
    """Create an ordered list of steps to complete the task."""
    prompt = PLANNER_PROMPT.format(tools=TOOLS_DESCRIPTIONS, task=state["task"])
    response = llm.invoke([HumanMessage(content=prompt)])

    # Parse "1. ...\n2. ...\n3. ..." into a list of strings
    lines = [l.strip() for l in response.content.strip().splitlines() if l.strip()]
    steps = [l for l in lines if l and l[0].isdigit()]  # keep numbered lines

    print(f"\n── Plan ─────────────────────────────────────────────────")
    for step in steps:
        print(f"  {step}")
    print("─────────────────────────────────────────────────────────")

    return {"plan": steps, "step_index": 0, "step_results": []}


# ─── Node 2: executor ──────────────────────────────────────────────────────────
# The executor handles ONE step at a time. It uses the LLM to decide which tool
# to call for the current step, executes it, and records the result.
EXECUTOR_PROMPT = """\
You are an executor. You must complete ONE step of a research plan.

{tools}

Context so far (previous step results):
{context}

Current step to execute: {current_step}

Call the appropriate tool for this step and return the raw result.
If no tool is needed, answer directly.
Return ONLY the result — no extra commentary."""

def executor_node(state: PlanExecuteState) -> dict:
    """Execute the current step in the plan."""
    idx     = state["step_index"]
    step    = state["plan"][idx]
    context = "\n".join(
        f"Step {i+1} result: {r}"
        for i, r in enumerate(state["step_results"])
    ) or "None yet."

    prompt = EXECUTOR_PROMPT.format(
        tools=TOOLS_DESCRIPTIONS,
        context=context,
        current_step=step,
    )

    # Give the executor access to tools so it can actually call them
    tools_list = [lookup_statistic, calculate, compare]
    executor_llm = llm.bind_tools(tools_list)
    response = executor_llm.invoke([HumanMessage(content=prompt)])

    # If the model returned tool calls, run them and collect results
    if hasattr(response, "tool_calls") and response.tool_calls:
        results = []
        for tc in response.tool_calls:
            tool_name = tc["name"]
            tool_args = tc["args"]
            tool_map  = {t.name: t for t in tools_list}
            if tool_name in tool_map:
                raw = tool_map[tool_name].invoke(tool_args)
                results.append(str(raw))
                print(f"  [Tool: {tool_name}({tool_args})] → {raw}")
        step_result = " | ".join(results)
    else:
        step_result = response.content.strip()
        print(f"  [LLM reasoning] → {step_result}")

    updated_results = state["step_results"] + [f"Step {idx+1}: {step_result}"]
    return {"step_results": updated_results, "step_index": idx + 1}


# ─── Node 3: finalizer ─────────────────────────────────────────────────────────
FINALIZER_PROMPT = """\
You are writing the final answer to a research task.

Task: {task}

Here are all the results gathered step by step:
{results}

Write a clear, concise answer in 2-4 sentences. Be specific with numbers."""

def finalizer_node(state: PlanExecuteState) -> dict:
    """Synthesise all step results into one coherent final answer."""
    results_text = "\n".join(state["step_results"])
    prompt = FINALIZER_PROMPT.format(task=state["task"], results=results_text)
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_answer": response.content.strip()}


# ─── Router: are all steps done? ───────────────────────────────────────────────
def route_after_executor(state: PlanExecuteState) -> str:
    """
    If all steps in the plan have been executed → go to finalizer.
    Otherwise → loop back to executor for the next step.
    """
    if state["step_index"] >= len(state["plan"]):
        return "finalizer"
    return "executor"


# ─── Graph ─────────────────────────────────────────────────────────────────────
graph = StateGraph(PlanExecuteState)
graph.add_node("planner",   planner_node)
graph.add_node("executor",  executor_node)
graph.add_node("finalizer", finalizer_node)

graph.add_edge(START, "planner")
graph.add_edge("planner", "executor")
graph.add_conditional_edges("executor", route_after_executor, {
    "executor":  "executor",   # more steps → loop
    "finalizer": "finalizer",  # all steps done → finalize
})
graph.add_edge("finalizer", END)

app = graph.compile()


# ─── Run Examples ──────────────────────────────────────────────────────────────
def run(task: str, label: str) -> None:
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"Task: {task}")
    print("="*60)

    initial_state: PlanExecuteState = {
        "task":         task,
        "plan":         [],
        "step_index":   0,
        "step_results": [],
        "final_answer": "",
    }
    result = app.invoke(initial_state)

    print("\n── Step Results ─────────────────────────────────────────")
    for r in result["step_results"]:
        print(f"  {r}")

    print(f"\n── Final Answer ─────────────────────────────────────────")
    print(result["final_answer"])


if __name__ == "__main__":
    # Example 1: Simple two-step plan
    run(
        task="What is the population of France and Germany, and which country is larger?",
        label="Example 1 — Two-step plan (two lookups + compare)",
    )

    # Example 2: Multi-step plan requiring calculations
    run(
        task=(
            "Compare France and Germany by population density "
            "(population ÷ area in km²). Which is more densely populated and by how much?"
        ),
        label="Example 2 — Four-step plan (4 lookups + 2 divisions + compare)",
    )

    # Example 3: Three-country comparison
    run(
        task="Which of France, Germany, and Japan has the highest GDP per capita? Show the calculation.",
        label="Example 3 — Complex plan (6 lookups + 3 divisions + comparison)",
    )
