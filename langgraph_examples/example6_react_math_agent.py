# file: langgraph_examples/example6_react_math_agent.py
"""
ReAct Math Agent — find_sum + find_product
─────────────────────────────────────────
A minimal ReAct agent that uses ONLY tools for math. The system prompt instructs
the LLM to "use only tools available" and "do not solve the problem yourself" —
so the agent must call find_sum or find_product instead of computing in its head.

This example demonstrates:
  - @tool with docstrings: The LLM reads them to decide which tool to call.
  - System prompt (state_modifier): Shapes agent behavior — here, forces tool use.
  - ReAct loop: User → Agent (tool_calls) → Tools (execute) → Agent (final answer).
  - Parallel tool calls: "3×2 and 5+1" can trigger find_product AND find_sum in one turn.

Flow: HumanMessage → Agent (returns AIMessage with tool_calls) → ToolNode runs tools
→ ToolMessages appended → Agent (sees results, returns final AIMessage with content).
"""

# ─── Imports ───────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# load_dotenv() reads .env and sets OPENAI_API_KEY so ChatOpenAI can authenticate
load_dotenv()

# ─── Tools ─────────────────────────────────────────────────────────────────────
# The @tool decorator turns a plain Python function into a LangChain tool. The LLM
# receives a schema (name, description, parameters) derived from the function
# signature and docstring. The docstring is critical: the LLM uses it to decide
# WHEN to call the tool and WHAT it does. Without a clear docstring, the agent
# may never call it or may call it incorrectly.

@tool
def find_sum(x: int, y: int) -> int:
    """
    Add two numbers and return their sum.
    Takes two integers as inputs and returns an integer.
    Use for any addition question.
    """
    return x + y


@tool
def find_product(x: int, y: int) -> int:
    """
    Multiply two numbers and return their product.
    Takes two integers as inputs and returns an integer.
    Use for any multiplication question.
    """
    return x * y


# ─── Build ReAct Agent ─────────────────────────────────────────────────────────
tools = [find_sum, find_product]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# bind_tools() injects the tool schemas into the LLM's context. Without this, the
# model would not know the tools exist and would never return tool_calls. When it
# wants to use a tool, it returns an AIMessage with tool_calls instead of content.
llm_with_tools = llm.bind_tools(tools)

# SystemMessage sets the "system" role — instructions that shape how the model
# behaves. Here we force it to use tools: without this, the model might compute
# 2+3 in its head and never call find_sum. Prepending this to every call ensures
# the agent always follows the "use only tools" rule.
system_prompt = SystemMessage(content="""You are a Math genius who can solve math problems.
Solve the problems provided by the user by using ONLY the tools available.
Do NOT solve the problem yourself — always call the appropriate tool.""")


def agent_node(state: MessagesState) -> dict:
    """
    Agent node: the LLM "reasoning" step in the ReAct loop.
    - Reads state["messages"] (conversation so far: user query, maybe tool results)
    - Prepends system_prompt so the model sees instructions first
    - Invokes the LLM; it may return either:
      a) AIMessage(content="...") — final answer, no tool_calls → graph goes to END
      b) AIMessage(tool_calls=[...]) — wants to call tools → graph goes to "tools"
    - Returns {"messages": [response]} — MessagesState appends this to the list
    """
    messages = [system_prompt] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# ─── Graph Structure ─────────────────────────────────────────────────────────
# StateGraph(MessagesState) — state has a single field "messages" (list of
# HumanMessage, AIMessage, ToolMessage). The add_messages annotation means new
# messages are appended, not replaced.
graph = StateGraph(MessagesState)

# Two nodes: agent (LLM) and tools (executes tool_calls)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))  # ToolNode runs tool_calls from last message

# Flow: START → agent → [conditional] → tools (if tool_calls) or END (if done)
graph.add_edge(START, "agent")

# tools_condition inspects the last message: if it has tool_calls → route to
# "tools"; otherwise → route to END. This is the "router" in the ReAct loop.
graph.add_conditional_edges("agent", tools_condition)

# After tools run, we loop back to agent so it can see the ToolMessage results
# and decide: call more tools, or give a final answer.
graph.add_edge("tools", "agent")

# compile() turns the graph definition into a runnable app (invoke, stream, etc.)
app = graph.compile()

# ─── Run Examples ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Example 1: Single tool call. The agent will call find_sum(2, 3) and return "5".
    print("=" * 60)
    print("Example 1: What is the sum of 2 and 3?")
    print("=" * 60)
    # invoke() runs the graph. Input: {"messages": [HumanMessage(...)]}
    # Output: result["messages"] = [HumanMessage, AIMessage(tool_calls), ToolMessage, AIMessage]
    result = app.invoke({"messages": [HumanMessage(content="what is the sum of 2 and 3?")]})
    # The last message is the final AIMessage with the answer (no tool_calls)
    print(f"Agent returned: {result['messages'][-1].content}\n")

    # pretty_repr() shows each message in a readable format — useful for debugging
    # the ReAct loop (HumanMessage → AIMessage w/ tool_calls → ToolMessage → AIMessage)
    print("Step-by-step execution:")
    for msg in result["messages"]:
        print(msg.pretty_repr())

    # Example 2: Parallel tool calls. The agent can call find_product AND find_sum
    # in a single turn — both ToolMessages are appended before the agent responds.
    print("\n" + "=" * 60)
    print("Example 2: What is 3 multiplied by 2 and 5 + 1?")
    print("=" * 60)
    result = app.invoke({"messages": [HumanMessage(content="What is 3 multiplied by 2 and 5 + 1?")]})
    print(f"Agent returned: {result['messages'][-1].content}\n")

    print("Step-by-step execution:")
    for msg in result["messages"]:
        print(msg.pretty_repr())
