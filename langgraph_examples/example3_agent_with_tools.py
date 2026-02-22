# file: langgraph_examples/example3_agent_with_tools.py
"""
Agent with Tools (ReAct Pattern)
────────────────────────────────
An agent is an LLM that can decide to call tools (calculator, database, API) and use
the results to answer. This example implements the ReAct pattern: Reason (LLM thinks)
→ Act (calls tool) → Observe (gets result) → Reason again → ... → Final answer.

Graph flow:
    START → agent → [tools_condition] → tools (if tool_calls) OR END (if done)
                      ↑                    |
                      └────────────────────┘
    The tools node always routes back to agent so the LLM can process tool results
    and decide whether to call more tools or give a final answer.

Key components:
  - @tool: Decorator that turns a Python function into a LangChain tool. The LLM
    reads the function name and docstring to decide when and how to call it.
  - llm.bind_tools(tools): Gives the LLM awareness of available tools. When it wants
    to use one, it returns an AIMessage with tool_calls instead of plain text.
  - ToolNode: Pre-built node that executes tool_calls from the last message and
    returns ToolMessages with the results.
  - tools_condition: Pre-built router that checks the last message — if it has
    tool_calls, route to "tools"; otherwise route to END.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool          # Decorator to make a function into a LangGraph tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# ─── Step 1: Define Tools ─────────────────────────────────────────────────────
# A tool is a Python function decorated with @tool. LangChain converts it into a
# schema (name, description, parameters) that the LLM receives. The LLM uses the
# docstring and parameter types to decide WHEN to call the tool and WHAT arguments
# to pass. Write clear, descriptive docstrings — they directly affect tool selection!

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together. Use this for any addition calculation."""
    result = a + b
    print(f"[TOOL] add_numbers({a}, {b}) = {result}")
    return result

@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together. Use this for any multiplication."""
    result = a * b
    print(f"[TOOL] multiply_numbers({a}, {b}) = {result}")
    return result

@tool
def get_paper_info(paper_title: str) -> str:
    """
    Look up information about a research paper by title.
    Returns the abstract and key findings.
    Use this when asked about specific academic papers.
    """
    # In a real system, this would query an academic database like Semantic Scholar
    # For this example, we return mock data
    mock_database = {
        "attention is all you need": """
            Authors: Vaswani et al. (2017)
            Abstract: We propose a new network architecture, the Transformer, 
            based solely on attention mechanisms. The model achieves 28.4 BLEU 
            on WMT 2014 English-to-German translation task.
            Key finding: Attention mechanisms alone are sufficient for sequence modeling,
            outperforming RNNs and CNNs.
        """,
        "bert": """
            Authors: Devlin et al. (2018)
            Abstract: BERT (Bidirectional Encoder Representations from Transformers)
            is designed to pre-train deep bidirectional representations.
            Key finding: Pre-training on large corpora and fine-tuning achieves 
            state-of-the-art results on 11 NLP tasks.
        """
    }
    
    key = paper_title.lower().strip()
    if key in mock_database:
        print(f"[TOOL] Found paper: {paper_title}")
        return mock_database[key]
    else:
        return f"Paper '{paper_title}' not found in database."

# ─── Step 2: Set Up the LLM with Tools ───────────────────────────────────────
tools = [add_numbers, multiply_numbers, get_paper_info]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# bind_tools(tools) injects tool schemas into the LLM's context. The model now
# knows: "I can call add_numbers, multiply_numbers, get_paper_info." When it decides
# to use a tool, it returns an AIMessage with a tool_calls field (structured JSON)
# instead of content. The graph then routes to ToolNode to execute those calls.
llm_with_tools = llm.bind_tools(tools)

# ─── Step 3: Define Nodes ─────────────────────────────────────────────────────

def agent_node(state: MessagesState) -> dict:
    """
    The "brain" node. Invokes the LLM with the full message history.
    The LLM can respond in two ways:
      1. Plain text (content) → tools_condition routes to END → we're done.
      2. Tool calls (tool_calls) → tools_condition routes to "tools" → ToolNode
         runs the tools, appends ToolMessages, and we loop back to agent.
    On subsequent passes, state["messages"] includes the new ToolMessages, so the
    LLM sees the tool results and can either call more tools or give a final answer.
    """
    print(f"\n[AGENT] Thinking... ({len(state['messages'])} messages in history)")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# ToolNode: Pre-built LangGraph node that handles tool execution.
# 1. Reads the last message's tool_calls (list of {name, args})
# 2. Invokes each tool with the given args
# 3. Returns ToolMessage objects with the results (appended to state via add_messages)
tools_node = ToolNode(tools)

# ─── Step 4: Define the Routing Logic ─────────────────────────────────────────
# After the agent runs, we must decide: tool call or final answer?
# tools_condition(last_message) returns "tools" if tool_calls exist, else "__end__".
# This creates the ReAct loop: agent → tools → agent → ... until the agent
# responds with plain text (no tool_calls).

# ─── Step 5: Build the Graph ──────────────────────────────────────────────────
# Graph structure:
#   START → agent → [conditional] → tools (if tool_calls) ─┐
#                └→ END (if no tool_calls)                 │
#                                                          └→ agent (loop)
graph = StateGraph(MessagesState)

# Add nodes
graph.add_node("agent", agent_node)
graph.add_node("tools", tools_node)

# Add edges
graph.add_edge(START, "agent")

# Conditional edge from agent:
# tools_condition checks the last message and routes accordingly
graph.add_conditional_edges(
    "agent",           # From this node
    tools_condition,   # Use this function to decide
    # The function returns "tools" or "__end__"
    # "__end__" is the string version of END
)

# After tools run, always go back to agent (so it can use the tool results)
graph.add_edge("tools", "agent")

app = graph.compile()

# ─── Step 6: Run Tests ─────────────────────────────────────────────────────────
# Three scenarios: math only, paper lookup only, and multi-step (both in one query).
from langchain_core.messages import HumanMessage

print("=" * 60)
print("Test 1: Math calculation")
print("=" * 60)
result = app.invoke({
    "messages": [HumanMessage(content="What is 127 multiplied by 34? Show me the steps.")]
})
print(f"\nFinal Answer: {result['messages'][-1].content}")

print("\n" + "=" * 60)
print("Test 2: Paper lookup")
print("=" * 60)
result = app.invoke({
    "messages": [HumanMessage(content="Tell me about the paper 'Attention is All You Need'")]
})
print(f"\nFinal Answer: {result['messages'][-1].content}")

print("\n" + "=" * 60)
print("Test 3: Multi-step (math + paper)")
print("=" * 60)
result = app.invoke({
    "messages": [HumanMessage(content="""
    I need two things:
    1. What is 15.5 + 27.3?
    2. Summarize what BERT is about
    """)]
})
print(f"\nFinal Answer: {result['messages'][-1].content}")