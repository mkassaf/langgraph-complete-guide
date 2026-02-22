# file: langgraph_examples/example4_multi_agent_supervisor.py
"""
Multi-Agent System with a Supervisor
────────────────────────────────────
Instead of one general-purpose agent, we have SPECIALIZED agents (math, research,
writing) managed by a SUPERVISOR that decides which specialist to call next.

Architecture:
    User → Supervisor → [math_agent | research_agent | writing_agent] → Supervisor
         ↑                    ↓ (tools)                                    |
         |              [math_tools | research_tools | writing_tools]      |
         |                    ↓ (back to agent)                             |
         └─────────────────────────────────────────────────────────────────┘

Flow: Supervisor reads the conversation and picks an agent (or FINISH). The agent
runs, may call its tools, then control returns to the supervisor. The supervisor
decides again: call another agent (e.g. for a different sub-task) or FINISH.

Key concepts:
  - SupervisorState: Extends MessagesState with a "next" field. The supervisor
    writes state["next"] = "math_agent" | "research_agent" | "writing_agent" | "FINISH".
  - with_structured_output(RoutingDecision): Forces the LLM to return a Pydantic
    object (reasoning, next) instead of free text — ensures valid routing.
  - make_agent(): Factory that creates agent nodes with different tools + system prompts.
  - Separate tool nodes per agent: Each agent has its own ToolNode so tools don't
    get mixed (math_agent shouldn't call search_literature).
"""

import os
from typing import Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# ─── The LLMs ─────────────────────────────────────────────────────────────────
# We use different LLM instances for different agents.
# In practice you might use different models or different system prompts.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ─── Specialized Tools for Each Agent ─────────────────────────────────────────
# Each agent gets ONLY the tools it needs. math_agent has calculate; research_agent
# has search_literature; writing_agent has improve_writing. This keeps agents focused
# and prevents the math agent from accidentally calling the literature search.

@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.
    Input should be a valid Python math expression as a string.
    Example: '2 ** 10', '(15 + 7) * 3', 'round(3.14159 * 5**2, 2)'
    """
    try:
        # eval with restricted context for safety
        allowed_names = {"__builtins__": {}, "round": round, "abs": abs,
                        "max": max, "min": min, "sum": sum}
        result = eval(expression, allowed_names)
        print(f"[MATH TOOL] {expression} = {result}")
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool
def search_literature(query: str) -> str:
    """
    Search academic literature for a topic.
    Returns a summary of relevant findings.
    Use for: finding papers, understanding research landscape, getting citations.
    """
    # Mock database — in real usage, connect to Semantic Scholar, ArXiv API, etc.
    mock_results = {
        "transformer": "Transformers (Vaswani 2017) revolutionized NLP using self-attention. Follow-ups include BERT (Devlin 2018), GPT series (OpenAI), and T5 (Raffel 2020).",
        "reinforcement learning": "RL involves an agent learning by interacting with an environment. Key algorithms: Q-Learning, PPO (Schulman 2017), SAC (Haarnoja 2018). Recent: RLHF (Christiano 2017) for LLM alignment.",
        "graph neural network": "GNNs operate on graph-structured data. Key papers: GCN (Kipf 2017), GraphSAGE (Hamilton 2017), GAT (Veličković 2018). Applications in drug discovery, social networks, knowledge graphs.",
    }
    
    for keyword, info in mock_results.items():
        if keyword in query.lower():
            print(f"[RESEARCH TOOL] Found results for: {query}")
            return info
    
    return f"Limited results for '{query}'. Consider searching ArXiv directly."

@tool
def improve_writing(text: str, style: str = "academic") -> str:
    """
    Improve the quality of a text passage.
    Styles: 'academic' (formal, precise), 'clear' (simple, accessible), 
            'concise' (shorter, tighter).
    """
    # In a real system, this would call an LLM with specific writing instructions.
    # Here we simulate with a mock response.
    print(f"[WRITING TOOL] Improving text in '{style}' style...")
    return f"[Improved version in '{style}' style]: {text[:50]}... [The writing has been improved for clarity and flow.]"

# ─── Define Each Specialized Agent ────────────────────────────────────────────
# make_agent is a factory: given an LLM, a list of tools, and a system prompt,
# it returns a node function. Each agent gets its own identity via the system
# prompt ("You are a mathematics expert...") and its own tools. The agent sees
# the full message history (including other agents' responses) so it can collaborate.

def make_agent(llm, tools_list, system_prompt):
    """
    Factory: creates a node function for a specialized agent.
    Returns a function (state) -> {"messages": [response]} that invokes the LLM
    with the system prompt + conversation history. The LLM can respond with text
    or tool_calls; tools_condition routes accordingly.
    """
    agent_llm = llm.bind_tools(tools_list)
    
    def agent_fn(state: MessagesState) -> dict:
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = agent_llm.invoke(messages)
        return {"messages": [response]}
    
    return agent_fn

# Create the three specialized agents
math_agent = make_agent(
    llm=llm,
    tools_list=[calculate],
    system_prompt="""You are a mathematics and statistics expert.
    You help with calculations, statistical analysis, and mathematical proofs.
    Always use the calculate tool for numerical computations.
    Show your reasoning step by step."""
)

research_agent = make_agent(
    llm=llm,
    tools_list=[search_literature],
    system_prompt="""You are an academic research assistant.
    You help find relevant papers, summarize research areas, and suggest citations.
    Always search the literature before answering research questions.
    Provide specific paper references when available."""
)

writing_agent = make_agent(
    llm=llm,
    tools_list=[improve_writing],
    system_prompt="""You are an academic writing expert.
    You help improve clarity, structure, and style of academic writing.
    Use the improve_writing tool to enhance text passages."""
)

# ─── The Supervisor ───────────────────────────────────────────────────────────
# The supervisor is the "orchestrator": it reads the conversation and decides
# WHO should act next. Unlike free-text output, we need a structured choice so we
# can route. We use with_structured_output(RoutingDecision) so the LLM returns
# a Pydantic object with .next = "math_agent" | "research_agent" | "writing_agent" | "FINISH".
# We store this in state["next"]; route_from_supervisor reads it for the conditional edge.

from typing import TypedDict
from langgraph.graph.message import add_messages
from typing import Annotated

class SupervisorState(TypedDict):
    """
    State for the multi-agent graph. Extends the usual messages list with:
      - messages: Conversation history (HumanMessage, AIMessage, ToolMessage, etc.)
      - next: Routing target. Written by supervisor; read by route_from_supervisor.
    The "next" field is required for conditional edges — we need a string to map
    to node names. "FINISH" maps to END.
    """
    messages: Annotated[list, add_messages]
    next: str  # "math_agent" | "research_agent" | "writing_agent" | "FINISH"

# with_structured_output forces the LLM to return a RoutingDecision object.
from pydantic import BaseModel

class RoutingDecision(BaseModel):
    """The supervisor's decision about which agent to call next."""
    reasoning: str   # Why the supervisor made this choice (for transparency)
    next: Literal["math_agent", "research_agent", "writing_agent", "FINISH"]

supervisor_llm = llm.with_structured_output(RoutingDecision)

def supervisor_node(state: SupervisorState) -> dict:
    """
    The supervisor reads the conversation and decides which specialist to call,
    or whether the task is complete.
    """
    system_prompt = """You are a research team supervisor coordinating specialized agents:
    
    - math_agent: For calculations, statistics, mathematical analysis
    - research_agent: For finding papers, understanding research landscape
    - writing_agent: For improving text quality, academic writing
    - FINISH: When the user's question has been fully answered
    
    Based on the conversation, decide who should act next.
    If the last agent has provided a complete answer, choose FINISH.
    """
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    decision = supervisor_llm.invoke(messages)
    
    print(f"\n[SUPERVISOR] Routing to: {decision.next}")
    print(f"[SUPERVISOR] Reason: {decision.reasoning}")
    
    return {"next": decision.next}

# ─── Routing Function for Supervisor ──────────────────────────────────────────

def route_from_supervisor(state: SupervisorState) -> str:
    """
    Routing function for the conditional edge from supervisor.
    Returns the key that maps to the next node: "math_agent", "research_agent",
    "writing_agent", or "FINISH" (which maps to END in the path map).
    """
    return state["next"]

# ─── Build the Multi-Agent Graph ──────────────────────────────────────────────
# Nodes: supervisor, math_agent, research_agent, writing_agent, math_tools,
#        research_tools, writing_tools.
graph = StateGraph(SupervisorState)

# Add the supervisor
graph.add_node("supervisor", supervisor_node)

# Add each specialized agent
graph.add_node("math_agent", math_agent)
graph.add_node("research_agent", research_agent)
graph.add_node("writing_agent", writing_agent)

# Add tool nodes for each agent's tools
graph.add_node("math_tools", ToolNode([calculate]))
graph.add_node("research_tools", ToolNode([search_literature]))
graph.add_node("writing_tools", ToolNode([improve_writing]))

# ─── Wire the Edges ───────────────────────────────────────────────────────────
# Edge logic:
#   1. START → supervisor (always)
#   2. supervisor → agent or END (conditional: route_from_supervisor)
#   3. agent → tools or supervisor (conditional: tools_condition)
#      - If agent returns tool_calls → go to that agent's tool node
#      - If agent returns plain text → go back to supervisor (which may pick
#        another agent for a follow-up, or FINISH)
#   4. tools → agent (always; agent processes tool results and may call more tools)

# Start: always go to supervisor first
graph.add_edge(START, "supervisor")

# From supervisor: route to the chosen agent (or END)
graph.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "math_agent": "math_agent",
        "research_agent": "research_agent",
        "writing_agent": "writing_agent",
        "FINISH": END,
    }
)

# Each agent: tools_condition returns "tools" or "__end__". We map:
#   "tools" → this agent's tool node (math_tools, research_tools, writing_tools)
#   "__end__" → supervisor (agent gave a text response; supervisor decides next)
graph.add_conditional_edges("math_agent", tools_condition, 
                            {"tools": "math_tools", "__end__": "supervisor"})
graph.add_conditional_edges("research_agent", tools_condition,
                            {"tools": "research_tools", "__end__": "supervisor"})
graph.add_conditional_edges("writing_agent", tools_condition,
                            {"tools": "writing_tools", "__end__": "supervisor"})

# After each tool runs → back to its agent
graph.add_edge("math_tools", "math_agent")
graph.add_edge("research_tools", "research_agent")
graph.add_edge("writing_tools", "writing_agent")

app = graph.compile()

# ─── Test the Multi-Agent System ──────────────────────────────────────────────
# We pass "next": "" because SupervisorState requires it. The supervisor will
# overwrite it with its routing decision. For multi-part queries (math + research),
# the supervisor may route to math_agent first, then back to supervisor, then to
# research_agent, etc., until it chooses FINISH.

def run_query(query: str):
    print("\n" + "=" * 65)
    print(f"QUERY: {query}")
    print("=" * 65)
    result = app.invoke({
        "messages": [HumanMessage(content=query)],
        "next": ""
    })
    print(f"\nFINAL ANSWER:\n{result['messages'][-1].content}")

run_query("What is 2^32 and what are transformer neural networks?")
run_query("Find papers on graph neural networks and calculate how many citations a paper gets per year if it has 450 citations in 3 years.")