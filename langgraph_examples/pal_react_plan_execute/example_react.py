# file: langgraph_examples/pal_react_plan_execute/example_react.py
"""
ReAct — Reasoning + Acting in LangGraph
─────────────────────────────────────────
ReAct (from the 2022 paper "ReAct: Synergizing Reasoning and Acting in Language Models")
interleaves THINKING with DOING in a continuous loop.

The pattern per iteration:
  Thought  → The model reasons about what to do next (internal, implicit in LLMs)
  Action   → The model calls a tool
  Observation → The tool returns a result
  (repeat until the model has enough information to answer)

Key difference from PAL:
  PAL   — One shot: write code → run code → answer.  No loop, no branching.
  ReAct — Dynamic loop: the agent decides WHICH tool to call based on
           what it has already observed.  Can call many different tools in any order.

Key difference from Plan-and-Execute:
  ReAct          — No explicit plan.  The agent reasons and acts one step at a time,
                   dynamically adapting as results come in.
  Plan-and-Execute — A full plan is written FIRST, then steps are executed in order.
                   Replanning only happens if something fails.

Tools in this example:
  calculator(expr)  — evaluates a math expression (Python eval, safe subset)
  lookup_fact(topic) — returns a pre-loaded "database" fact (simulates web search)
  get_unit_price(item) — returns the price of an item from a price table

Graph:
  START → [agent] ⇄ [tools] → END
  (tools_condition routes agent→tools when tool_calls exist, else agent→END)
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# ─── Tools ─────────────────────────────────────────────────────────────────────

@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.
    Input must be a valid Python math expression string, e.g. '23 * 47' or '(100 - 25) / 4'.
    Use this for any arithmetic: addition, subtraction, multiplication, division, powers.
    """
    # Only allow safe operations — no imports, no builtins abuse
    allowed = {"__builtins__": {}, "abs": abs, "round": round, "pow": pow, "min": min, "max": max}
    try:
        result = eval(expression, allowed)
        return str(result)
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


# Simulated fact database — in a real agent this would call a search API
FACTS_DB = {
    "eiffel tower height":      "The Eiffel Tower is 330 metres (1,083 feet) tall.",
    "speed of light":           "The speed of light in a vacuum is approximately 299,792,458 metres per second.",
    "population of france":     "France has a population of approximately 68 million people.",
    "population of germany":    "Germany has a population of approximately 84 million people.",
    "area of brazil":           "Brazil covers an area of 8,515,767 square kilometres.",
    "amazon river length":      "The Amazon River is approximately 6,400 kilometres long.",
    "water boiling point":      "Water boils at 100°C (212°F) at sea level.",
}

@tool
def lookup_fact(topic: str) -> str:
    """
    Look up a factual piece of information about a topic.
    Use this to find facts like heights, populations, distances, speeds, or scientific constants.
    Input should be a short descriptive phrase, e.g. 'eiffel tower height' or 'speed of light'.
    """
    key = topic.lower().strip()
    # Try exact match first, then partial match
    if key in FACTS_DB:
        return FACTS_DB[key]
    for db_key, val in FACTS_DB.items():
        if key in db_key or db_key in key:
            return val
    return f"No fact found for '{topic}'. Try a different phrasing."


PRICE_DB = {
    "apple":    1.25,
    "orange":   0.80,
    "banana":   0.45,
    "notebook": 3.50,
    "pen":      1.10,
}

@tool
def get_unit_price(item: str) -> str:
    """
    Get the unit price of an item from the store catalogue.
    Returns the price in USD for one unit of the item.
    Use this before calculating total costs for purchases.
    Input should be the item name, e.g. 'apple' or 'notebook'.
    """
    key = item.lower().strip()
    if key in PRICE_DB:
        return f"The unit price of '{item}' is ${PRICE_DB[key]:.2f}."
    return f"Item '{item}' not found in catalogue. Available: {', '.join(PRICE_DB.keys())}."


# ─── Agent ─────────────────────────────────────────────────────────────────────
tools = [calculator, lookup_fact, get_unit_price]
llm   = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# The system prompt asks the model to reason step-by-step (Thought) before acting.
# This mirrors the original ReAct paper's explicit Thought/Action/Observation format.
SYSTEM_PROMPT = SystemMessage(content="""\
You are a helpful research assistant. You have access to tools for facts, prices, and math.

Follow the ReAct pattern strictly:
1. THINK about what information you need and which tool to use.
2. CALL the appropriate tool.
3. READ the tool result (observation).
4. Repeat steps 1-3 until you have everything you need.
5. Give the final answer only when all calculations are complete.

Never guess facts or do math in your head — always use the tools.""")


def agent_node(state: MessagesState) -> dict:
    """
    The reasoning step: the LLM looks at the current conversation
    (user question + all previous tool results) and decides:
      a) call a tool  → AIMessage with tool_calls  → graph routes to 'tools'
      b) final answer → AIMessage with content text → graph routes to END
    """
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# ─── Graph ─────────────────────────────────────────────────────────────────────
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)  # tool_calls? → tools : END
graph.add_edge("tools", "agent")                       # loop back after each tool

app = graph.compile()


# ─── Helpers ───────────────────────────────────────────────────────────────────
def run_and_print(question: str, label: str) -> None:
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"Q: {question}")
    print("="*60)

    result = app.invoke({"messages": [HumanMessage(content=question)]})

    print("\n── Full ReAct Trace ─────────────────────────────────────")
    for msg in result["messages"]:
        print(msg.pretty_repr())

    print(f"\n── Final Answer ─────────────────────────────────────────")
    print(result["messages"][-1].content)


# ─── Examples ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Example 1: Single tool call — fact lookup only
    run_and_print(
        question="What is the population of France?",
        label="Example 1 — Single tool (fact lookup)",
    )

    # Example 2: Two tool calls — fact + calculator
    # The agent must: (1) look up Eiffel Tower height, (2) convert metres to feet using the formula
    run_and_print(
        question="How many feet tall is the Eiffel Tower? Show me the calculation.",
        label="Example 2 — Two tools chained (fact → calculator)",
    )

    # Example 3: Three tool calls — price lookup + calculator + reasoning
    # The agent must: (1) get apple price, (2) get orange price, (3) calculate total for a basket
    run_and_print(
        question="I want to buy 12 apples and 8 oranges. How much will that cost in total?",
        label="Example 3 — Three tool calls (price×2 → calculator)",
    )

    # Example 4: Multi-step reasoning — compare two facts then calculate
    run_and_print(
        question="How many more people does Germany have than France? Express as a percentage of France's population.",
        label="Example 4 — Adaptive reasoning (two lookups → two calculations)",
    )
