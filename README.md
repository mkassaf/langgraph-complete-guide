# LangGraph Complete Guide for Researchers
## From Zero to Multi-Agent Systems

> **Who this is for:** PhD students and researchers with Python knowledge but zero LangGraph/LangChain experience.
> **Goal:** Build progressively more complex AI agent systems using the latest LangGraph (2025).

All examples live in the [`langgraph_examples/`](langgraph_examples/) folder.

**Keywords:** LangGraph, LangChain, AI agents, LLM, multi-agent systems, OpenAI, Python, research assistant, ReAct, tools, chatbot, supervisor pattern, tutorial

---

## Table of Contents

- **[Python Prerequisites](README_PREREQUISITES.md)** — New to Python? Quick refresher on variables, functions, dicts, type hints, and decorators.
- **[LangChain Tutorial](README_LANGCHAIN.md)** — New to LangChain? Learn models, prompts, chains, and tools first.

1. [What is LangGraph? (Conceptual Overview)](#1-what-is-langgraph)
2. [Environment Setup](#2-environment-setup)
3. [Core Concepts You Must Understand First](#3-core-concepts)
4. [Example 1 — Hello World Graph (Pure LangGraph, No LLM)](#4-example-1-hello-world-graph)
5. [Example 2 — Simple Chatbot with a Real LLM](#5-example-2-simple-chatbot)
6. [Example 3 — Agent with Tools (ReAct Pattern)](#6-example-3-agent-with-tools)
7. [Example 4 — Multi-Agent System with a Supervisor](#7-example-4-multi-agent-supervisor)
8. [Example 5 — Research Multi-Agent System (Full Pipeline)](#8-example-5-research-pipeline)
9. [Debugging and Visualization Tips](#9-debugging-tips)
10. [Quick Reference Cheat Sheet](#10-cheat-sheet)

---

## 1. What is LangGraph?

Imagine you are designing a research workflow:

1. A student reads a paper.
2. They summarize it.
3. They check if the summary is good enough — if not, they re-read.
4. Once good, they write a critique.

This is not a straight line. It has **loops**, **decisions**, and **multiple actors**. Traditional code (if/else chains) gets messy fast. LangGraph solves this.

**LangGraph is a Python library** that lets you define AI workflows as a **graph** — a set of **nodes** (actions/functions) connected by **edges** (transitions). The key superpower is:

- **State**: Every node reads a shared "state" object and returns updates to it.
- **Cycles**: Unlike simple pipelines, graphs can loop (the agent tries again if it fails).
- **Multiple Agents**: Different nodes can be different AI agents with different roles.
- **Human-in-the-loop**: You can pause the graph and wait for a human decision.

**LangChain vs LangGraph:**
- **LangChain** = A library of building blocks (LLM wrappers, prompt templates, tools). Think of it as LEGO pieces.
- **LangGraph** = The framework that orchestrates those pieces into a stateful workflow. Think of it as the instructions that say how to connect the LEGOs.
- You can use LangGraph **without** LangChain, but they work beautifully together.
- **New to LangChain?** See [README_LANGCHAIN.md](README_LANGCHAIN.md) for a step-by-step tutorial on models, prompts, chains, and tools.

---

## 2. Environment Setup

### Step 1: Create a Python Virtual Environment

Always use a virtual environment to keep dependencies isolated.

```bash
# Create a new project folder
mkdir my_langgraph_project
cd my_langgraph_project

# Create a virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt. This means you are inside the virtual environment.

### Step 2: Install Required Packages

```bash
# Install LangGraph (latest version)
pip install -U langgraph

# Install LangChain and OpenAI integration (we'll use OpenAI's GPT models)
pip install -U langchain langchain-openai langchain-core

# For environment variable management
pip install python-dotenv
```

To verify the installation worked:

```python
# Run this in a Python REPL (type 'python' in terminal)
import langgraph
print(langgraph.__version__)  # Should print a version number like 0.3.x
```

### Step 3: Get an API Key

LangGraph itself is free and open source. But to use a real LLM (like GPT-4), you need an API key.

**Option A: OpenAI (recommended for beginners)**
1. Go to https://platform.openai.com/
2. Create an account
3. Go to "API Keys" → "Create new secret key"
4. Copy the key (starts with `sk-...`)

**Option B: Anthropic Claude**
```bash
pip install langchain-anthropic
```

**Option C: Use a free local model via Ollama (no API key needed)**
```bash
# Install Ollama from https://ollama.ai
# Then pull a model:
# ollama pull llama3
pip install langchain-ollama
```

### Step 4: Set Up Your API Key Safely

Never hardcode API keys in your code. Use a `.env` file:

```bash
# Create a file named .env in your project folder
touch .env
```

Add this to `.env` (replace with your actual key):
```
OPENAI_API_KEY=sk-your-actual-key-here
```

Add `.env` to `.gitignore` so you never accidentally upload it:
```bash
echo ".env" >> .gitignore
```

---

## 3. Core Concepts

Before writing any code, understand these 4 fundamental ideas:

### 3.1 State — The Shared Memory

The **State** is a Python dictionary that travels through every node in the graph. Think of it as a whiteboard that all agents can read and write on.

You define what goes on the whiteboard upfront using `TypedDict`:

```python
from typing import TypedDict

class MyState(TypedDict):
    user_question: str    # The question from the user
    answer: str           # The answer generated by an agent
    is_complete: bool     # Whether we are done
```

Every node receives this state and returns a dictionary with only the fields it wants to update.

### 3.2 Nodes — The Actions

A **node** is just a Python function. It takes the current state and returns updates:

```python
def my_node(state: MyState) -> dict:
    # Read from state
    question = state["user_question"]
    
    # Do something (call an LLM, search the web, compute something)
    result = do_some_work(question)
    
    # Return only the fields you want to update
    return {"answer": result}
```

### 3.3 Edges — The Connections

**Edges** define what happens after a node finishes:

- **Normal edge**: Always go from node A to node B.
- **Conditional edge**: Look at the state and decide which node to go to next.

### 3.4 The Graph — Putting It Together

```
START → node_1 → node_2 → END
                    ↑         |
                    |_________|  (conditional: loop back if not done)
```

You build the graph by:
1. Creating a `StateGraph` with your state type
2. Adding nodes (functions)
3. Adding edges (connections)
4. Compiling it into a runnable app

---

## 4. Example 1 — Hello World Graph (No LLM)

Let's start with the simplest possible graph — no AI, just Python functions connected as a graph. This helps you understand the plumbing before adding complexity.

**What this does:** Takes a text string, passes it through two nodes that each append a letter, and returns the result.

```python
# file: langgraph_examples/example1_hello_world.py

# ─── Imports ─────────────────────────────────────────────────────────────────
from typing import TypedDict          # For defining our state structure
from langgraph.graph import StateGraph, START, END  # Core LangGraph components

# ─── Step 1: Define the State ─────────────────────────────────────────────────
# The state is a typed dictionary — it's like a contract that says 
# "our shared data will always have these fields with these types"

class State(TypedDict):
    text: str   # A simple string that nodes will modify

# ─── Step 2: Define Nodes (Functions) ─────────────────────────────────────────
# Each node is a function that:
#   - Takes the current state as input
#   - Returns a dict with the fields it wants to update

def node_a(state: State) -> dict:
    """Node A appends 'A' to the text."""
    current_text = state["text"]        # Read from state
    new_text = current_text + " → A"   # Do work
    print(f"Node A running. Text is now: '{new_text}'")
    return {"text": new_text}           # Return only what changed

def node_b(state: State) -> dict:
    """Node B appends 'B' to the text."""
    current_text = state["text"]
    new_text = current_text + " → B"
    print(f"Node B running. Text is now: '{new_text}'")
    return {"text": new_text}

def node_c(state: State) -> dict:
    """Node C appends 'C' to the text."""
    current_text = state["text"]
    new_text = current_text + " → C"
    print(f"Node C running. Text is now: '{new_text}'")
    return {"text": new_text}

# ─── Step 3: Build the Graph ──────────────────────────────────────────────────
# Create a StateGraph and tell it what our state looks like
graph = StateGraph(State)

# Add nodes: give each function a string name
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)

# Add edges: define the flow
# START is a special built-in constant meaning "the very beginning"
# END is a special built-in constant meaning "we are done"
graph.add_edge(START, "node_a")   # When graph starts, go to node_a
graph.add_edge("node_a", "node_b")  # After node_a, go to node_b
graph.add_edge("node_b", "node_c")  # After node_b, go to node_c
graph.add_edge("node_c", END)       # After node_c, we are done

# ─── Step 4: Compile the Graph ────────────────────────────────────────────────
# This "compiles" the graph definition into a runnable app
app = graph.compile()

# ─── Step 5: Run It ───────────────────────────────────────────────────────────
# invoke() runs the graph from START to END
# We provide the initial state as a dictionary
initial_state = {"text": "START"}
result = app.invoke(initial_state)

print("\n─── Final Result ───")
print(result)  # {'text': 'START → A → B → C'}
```

**Run it:**
```bash
python langgraph_examples/example1_hello_world.py
```

**Expected Output:**
```
Node A running. Text is now: 'START → A'
Node B running. Text is now: 'START → A → B'
Node C running. Text is now: 'START → A → B → C'

─── Final Result ───
{'text': 'START → A → B → C'}
```

**Key Takeaways:**
- The state dictionary flows through every node.
- Each node only updates the fields it cares about.
- The graph is compiled before running — compilation validates your graph structure.

---

## 5. Example 2 — Simple Chatbot with a Real LLM

Now let's add an actual LLM. We'll build a simple chatbot that remembers the conversation history.

**New concept introduced:** `MessagesState` — a built-in state type that manages a list of conversation messages automatically.

**Understanding `all_messages` and `SystemMessage`:**

- **`SystemMessage`** — A LangChain message type for the "system" role. It carries instructions that define the assistant's behavior (personality, rules, format). Chat APIs use three roles: `system` (instructions), `user` (`HumanMessage`), and `assistant` (`AIMessage`).

- **`all_messages = [system_msg] + state["messages"]`** — This builds the full message list sent to the LLM: `[system_msg, user_1, assistant_1, user_2, ...]`. The `+` operator concatenates the lists. The system message must be first so the model sees the instructions before the conversation.

- **Relation to "Context" in Generative AI** — In generative AI, **context** means everything the model can "see" when generating a response. LLMs are **stateless**: they have no memory. The only input they receive is the message list we send. So `all_messages` *is* the context — the full conversation history plus system instructions. Without passing the full history, the model would reply to each message in isolation and couldn't reference earlier turns. By passing it, we give the model the context it needs for coherent multi-turn dialogue. (Context size is limited by the model's context window, e.g. 128K tokens.)

```python
# file: langgraph_examples/example2_chatbot.py

# ─── Imports ─────────────────────────────────────────────────────────────────
import os
from dotenv import load_dotenv

# LangChain components for talking to OpenAI
from langchain_openai import ChatOpenAI

# LangGraph components
from langgraph.graph import StateGraph, MessagesState, START, END

# LangChain message types
from langchain_core.messages import HumanMessage, SystemMessage

# ─── Load API Key ─────────────────────────────────────────────────────────────
load_dotenv()  # Reads your .env file and sets environment variables
# Now os.environ["OPENAI_API_KEY"] is automatically set

# ─── Understanding MessagesState ──────────────────────────────────────────────
# MessagesState is a built-in state type provided by LangGraph.
# It looks roughly like this:
#
#   class MessagesState(TypedDict):
#       messages: Annotated[list[AnyMessage], add_messages]
#
# The "add_messages" annotation is special — it tells LangGraph to APPEND
# new messages to the list instead of replacing the whole list.
# This is how conversation history is maintained automatically.

# ─── Set Up the LLM ───────────────────────────────────────────────────────────
# ChatOpenAI is a LangChain wrapper around OpenAI's chat API
llm = ChatOpenAI(
    model="gpt-4o-mini",   # A fast, cheap model — good for testing
    temperature=0.7,        # 0 = deterministic, 1 = creative. 0.7 is balanced
)

# ─── Define the Node ──────────────────────────────────────────────────────────
def chatbot_node(state: MessagesState) -> dict:
    """
    This node:
    1. Reads all messages from the state (conversation history)
    2. Sends them to the LLM
    3. Gets a response
    4. Returns the response as a new message to be added to history
    """
    # state["messages"] is a list of all messages so far
    # We prepend a system message to set the assistant's personality
    system_msg = SystemMessage(content="""
    You are a helpful research assistant for a PhD student.
    Be concise, precise, and always cite when you're uncertain.
    """)
    
    # Build the full message list: [system] + [all previous messages]
    all_messages = [system_msg] + state["messages"]
    
    # Call the LLM with the full conversation
    response = llm.invoke(all_messages)
    
    # Return the AI's response — it will be APPENDED to messages automatically
    # because of the add_messages annotation in MessagesState
    return {"messages": [response]}

# ─── Build the Graph ──────────────────────────────────────────────────────────
graph = StateGraph(MessagesState)

graph.add_node("chatbot", chatbot_node)

graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

app = graph.compile()

# ─── Run as a Multi-Turn Conversation ─────────────────────────────────────────
print("Simple Research Assistant Chatbot")
print("Type 'quit' to exit\n")

# We maintain the conversation history ourselves across turns
conversation_history = []

while True:
    user_input = input("You: ").strip()
    
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    
    if not user_input:
        continue
    
    # Add the user's message to history
    conversation_history.append(HumanMessage(content=user_input))
    
    # Run the graph with the full conversation history
    result = app.invoke({"messages": conversation_history})
    
    # result["messages"] now contains the full history including the new AI response
    # The last message is the AI's response
    ai_response = result["messages"][-1]
    
    print(f"Assistant: {ai_response.content}\n")
    
    # Update our history with the result (includes the AI response now)
    conversation_history = result["messages"]
```

**Run it:**
```bash
python langgraph_examples/example2_chatbot.py
```

**Example Interaction:**
```
You: What is the difference between supervised and unsupervised learning?
Assistant: Supervised learning trains models on labeled data...

You: Can you give me a concrete example from NLP?
Assistant: Building on the previous discussion, a great NLP example is...
```

Notice how the assistant remembers the previous question! That's the `messages` list doing its job.

---

## 6. Example 3 — Agent with Tools (ReAct Pattern)

An **agent** is an LLM that can decide to call **tools** (calculator, web search, database) and use the results to answer. This implements the **ReAct** pattern: **Reason** (LLM thinks) → **Act** (calls tool) → **Observe** (gets result) → Reason again → ... → final answer.

**Why tools?** LLMs can't do math reliably, can't query live data, and can't access external APIs. Tools let the agent extend its capabilities by calling Python functions. The LLM decides *when* and *which* tool to use based on the user's question.

**Graph flow:**
```
START → agent → [tools_condition] → tools (if tool_calls) OR END (if done)
                      ↑                    |
                      └────────────────────┘
```
The agent node invokes the LLM. If the LLM returns `tool_calls`, we route to the tools node, which executes them and appends `ToolMessage` results. Then we loop back to the agent so it can process the results and either call more tools or give a final text answer. The loop continues until the agent responds with plain text (no `tool_calls`).

**Key components:**
| Component | Purpose |
|-----------|---------|
| `@tool` | Decorator that turns a Python function into a LangChain tool. The LLM reads the docstring and parameters to decide when to call it. |
| `llm.bind_tools(tools)` | Injects tool schemas into the LLM's context. The model can then return `tool_calls` instead of plain text. |
| `ToolNode` | Pre-built node that executes `tool_calls` from the last message and returns `ToolMessage` objects. |
| `tools_condition` | Pre-built router: if the last message has `tool_calls` → route to `"tools"`; otherwise → route to `END`. |

```python
# file: langgraph_examples/example3_agent_with_tools.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool          # Decorator to make a function into a LangGraph tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# ─── Step 1: Define Tools ─────────────────────────────────────────────────────
# A "tool" is just a Python function decorated with @tool.
# The LLM reads the function name and docstring to decide when to use it.
# IMPORTANT: Write clear, descriptive docstrings — the LLM uses them!

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
# We collect all tools in a list
tools = [add_numbers, multiply_numbers, get_paper_info]

# Create the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# CRITICAL: Bind tools to the LLM. This tells the LLM what tools are available.
# When the LLM wants to use a tool, it returns a special "tool call" message
# instead of a regular text response.
llm_with_tools = llm.bind_tools(tools)

# ─── Step 3: Define Nodes ─────────────────────────────────────────────────────

def agent_node(state: MessagesState) -> dict:
    """
    The 'brain' node. Calls the LLM which decides:
    - Either answer directly (go to END)
    - Or call a tool (go to tools node)
    """
    print(f"\n[AGENT] Thinking... ({len(state['messages'])} messages in history)")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# ToolNode is a pre-built LangGraph node that:
# 1. Looks at the last message (which should have tool_calls)
# 2. Executes the requested tools
# 3. Returns the results as ToolMessages
tools_node = ToolNode(tools)

# ─── Step 4: Define the Routing Logic ─────────────────────────────────────────
# After the agent runs, we need to decide: did it want to use a tool, or is it done?
# tools_condition is a pre-built function that does exactly this:
# - If the last message has tool_calls → route to "tools"
# - Otherwise → route to END

# ─── Step 5: Build the Graph ──────────────────────────────────────────────────
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

# ─── Step 6: Test It ──────────────────────────────────────────────────────────
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
```

**What you'll see:**
```
[AGENT] Thinking... (1 messages in history)
[TOOL] multiply_numbers(127, 34) = 4318.0
[AGENT] Thinking... (3 messages in history)

Final Answer: 127 × 34 = 4,318
```

The graph automatically loops: Agent → Tool → Agent → Tool → Agent → END. You didn't write that loop explicitly — it emerges from the conditional edge. Each time the agent runs, `state["messages"]` grows: HumanMessage → AIMessage (with tool_calls) → ToolMessage(s) → AIMessage (final answer). The LLM sees the full history, including tool results, so it can reason over them and produce a coherent response.

---

## 7. Example 4 — Multi-Agent System with a Supervisor

Now we build a **multi-agent system**. Instead of one general-purpose agent, we have **specialized agents** (math, research, writing) managed by a **supervisor** that decides which specialist to call next.

**Why multi-agent?** A single agent with many tools can get confused or use the wrong one. Specialists are focused: the math agent only has `calculate`, the research agent only has `search_literature`. The supervisor orchestrates: for "What is 2^32 and what are transformers?", it routes to math_agent first, then research_agent, then FINISH.

**Architecture:**
```
User → Supervisor → [math_agent | research_agent | writing_agent] → Supervisor
     ↑                    ↓ (if tool_calls)                            |
     |              [math_tools | research_tools | writing_tools]      |
     |                    ↓ (back to agent)                            |
     └────────────────────────────────────────────────────────────────┘
```

**Flow:** Supervisor reads the conversation and picks an agent (or FINISH). The agent runs, may call its tools (agent → tools → agent loop), then returns to the supervisor. The supervisor decides again: call another agent for a different sub-task, or FINISH.

**Key components:**
| Component | Purpose |
|-----------|---------|
| `SupervisorState` | Extends messages with a `next` field. The supervisor writes `state["next"]` = `"math_agent"` \| `"research_agent"` \| `"writing_agent"` \| `"FINISH"`. |
| `with_structured_output(RoutingDecision)` | Forces the LLM to return a Pydantic object instead of free text — ensures valid routing (no parsing errors). |
| `make_agent(llm, tools, system_prompt)` | Factory that creates agent nodes. Each agent gets different tools and a different system prompt. |
| Separate tool nodes | Each agent has its own `ToolNode` (math_tools, research_tools, writing_tools) so tools don't get mixed. |

```python
# file: langgraph_examples/example4_multi_agent_supervisor.py

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

def make_agent(llm, tools_list, system_prompt):
    """
    Factory function: creates a node function for a specialized agent.
    This shows a clean pattern for creating multiple similar agents.
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
# The supervisor decides which agent to call next, or whether we are done.
# We use a special structured output approach: the supervisor returns a "next" field.

from typing import TypedDict
from langgraph.graph.message import add_messages
from typing import Annotated

class SupervisorState(TypedDict):
    """State that includes messages AND a 'next' field for routing."""
    messages: Annotated[list, add_messages]
    next: str  # Which agent to call next, or "FINISH"

# The supervisor uses structured output to decide routing
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
    """Returns the next node to visit based on supervisor's decision."""
    return state["next"]

# ─── Build the Multi-Agent Graph ──────────────────────────────────────────────
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

# Each agent: if it wants to use tools → go to its tool node, else → back to supervisor
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
```

**What you'll see:** For a multi-part query like "What is 2^32 and what are transformers?", the supervisor first routes to `math_agent`, which calls `calculate` and returns. Control goes back to the supervisor, which then routes to `research_agent` for the transformer question. Each agent only sees and uses its own tools. The supervisor loops until it chooses FINISH.

---

## 8. Example 5 — Research Multi-Agent Pipeline (Full System)

A **sequential pipeline** of four specialized agents that collaborate on a research task. Unlike the supervisor pattern (Example 4), this is a **fixed linear flow** — no conditional routing, no loops.

**Architecture:**
```
START → planner → searcher → analyzer → writer → END
```

**Agents:**
| Agent | Role |
|-------|------|
| Planner | Breaks the research question into 3-4 specific subtasks (investigable questions) |
| Searcher | For each subtask, calls `search_arxiv`, summarizes findings |
| Analyzer | Synthesizes all findings, identifies gaps and themes |
| Writer | Produces a polished research summary report |

**Key difference from Examples 2–4:** We use **structured state** (`ResearchState`) instead of `MessagesState`. Fields like `subtasks`, `literature_findings`, `analysis`, `final_report` are passed between agents. `Annotated[List[str], add]` means list fields are **appended** when nodes return updates (not overwritten). The search agent manually handles tool calls (one-shot) instead of using `ToolNode`; this keeps the pipeline simple.

```python
# file: langgraph_examples/example5_research_pipeline.py

import os
from typing import TypedDict, Annotated, List, Optional
from operator import add  # For list concatenation in state
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# ─── Rich State for Research Pipeline ─────────────────────────────────────────
# This state holds everything the research pipeline needs to track.
# Notice how different agents write to different parts of the state.

class ResearchState(TypedDict):
    # The original research question
    research_question: str
    
    # Planner's output: list of subtasks to address
    # Annotated[List[str], add] means: APPEND new items (don't overwrite)
    subtasks: Annotated[List[str], add]
    
    # Search Agent's findings for each subtask
    # Annotated[List[str], add] means: APPEND new findings
    literature_findings: Annotated[List[str], add]
    
    # Analysis Agent's synthesis
    analysis: str
    
    # Writer Agent's final output
    final_report: str
    
    # Track which step we're on (for monitoring)
    current_step: str

# ─── Tools ────────────────────────────────────────────────────────────────────

@tool
def search_arxiv(query: str) -> str:
    """
    Search ArXiv for recent papers on a topic.
    Returns titles, authors, and abstracts of relevant papers.
    """
    # In production: use the ArXiv API (pip install arxiv)
    # import arxiv
    # search = arxiv.Search(query=query, max_results=5)
    # return "\n".join([f"{r.title}: {r.summary[:200]}" for r in search.results()])
    
    # Mock response for this tutorial
    mock_responses = {
        "large language model": """
            Found 3 papers:
            1. "GPT-4 Technical Report" (OpenAI, 2023) - Describes GPT-4's capabilities and training.
            2. "Llama 2" (Touvron et al., 2023) - Open-source LLM with 70B parameters.
            3. "Mistral 7B" (Jiang et al., 2023) - Efficient 7B model outperforming larger models.
        """,
        "hallucination": """
            Found 3 papers:
            1. "TruthfulQA" (Lin et al., 2022) - Benchmark measuring LLM truthfulness.
            2. "Self-RAG" (Asai et al., 2023) - Model learns to retrieve and reflect.
            3. "Chain-of-Verification" (Dhuliawala et al., 2023) - LLM verifies its own answers.
        """,
    }
    
    for keyword, result in mock_responses.items():
        if keyword in query.lower():
            return result
    return f"Found limited results for '{query}'. Key papers may require specialized database access."

@tool
def analyze_gap(findings: str) -> str:
    """
    Analyze research findings to identify gaps and research opportunities.
    Input: a summary of literature findings.
    Output: identified research gaps and suggested directions.
    """
    return f"""Research Gap Analysis:
    Based on the provided findings, key gaps include:
    1. Lack of standardized evaluation benchmarks
    2. Limited cross-domain generalization studies  
    3. Computational efficiency in real-world deployment
    4. Long-term impact and societal implications need further study
    
    Suggested research directions:
    - Develop unified evaluation frameworks
    - Study domain adaptation techniques
    - Investigate model compression without capability loss
    """

# ─── Agent Nodes ──────────────────────────────────────────────────────────────

def planner_agent(state: ResearchState) -> dict:
    """
    Breaks the research question into specific subtasks.
    Runs ONCE at the start of the pipeline.
    """
    print(f"\n[PLANNER] Planning research for: {state['research_question']}")
    
    prompt = f"""You are a research planner. Break this research question into 3-4 specific subtasks:
    
    Research Question: {state['research_question']}
    
    Return ONLY a numbered list of subtasks. Each subtask should be a specific question to investigate.
    Example format:
    1. What are the current state-of-the-art methods for X?
    2. What are the key limitations of existing approaches?
    3. What evaluation metrics are used in this domain?
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Parse the numbered list into individual subtasks
    lines = response.content.strip().split("\n")
    subtasks = [line.strip() for line in lines 
                if line.strip() and line.strip()[0].isdigit()]
    
    print(f"[PLANNER] Created {len(subtasks)} subtasks")
    for i, task in enumerate(subtasks, 1):
        print(f"  {i}. {task}")
    
    return {
        "subtasks": subtasks,
        "current_step": "planning_complete"
    }

def search_agent(state: ResearchState) -> dict:
    """
    Searches literature for each subtask identified by the planner.
    """
    print(f"\n[SEARCH AGENT] Searching literature for {len(state['subtasks'])} subtasks")
    
    all_findings = []
    
    for i, subtask in enumerate(state["subtasks"], 1):
        print(f"  Searching subtask {i}: {subtask[:60]}...")
        
        prompt = f"""You are a research search agent. Search for information about:
        
        Subtask: {subtask}
        
        Use the search_arxiv tool to find relevant papers, then summarize the findings.
        Context - Overall research question: {state['research_question']}
        """
        
        # Give this agent the search tool
        search_llm = llm.bind_tools([search_arxiv])
        
        # We do a simple one-shot search here
        # (In production you'd loop until the agent is satisfied)
        response = search_llm.invoke([HumanMessage(content=prompt)])
        
        # If the LLM called a tool, execute it
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]
            search_result = search_arxiv.invoke(tool_call['args'])
            
            # Now synthesize the result
            synthesis = llm.invoke([
                HumanMessage(content=f"Subtask: {subtask}\nSearch results: {search_result}\nSummarize the key findings in 2-3 sentences.")
            ])
            finding = f"Subtask: {subtask}\nFindings: {synthesis.content}"
        else:
            finding = f"Subtask: {subtask}\nFindings: {response.content}"
        
        all_findings.append(finding)
    
    print(f"[SEARCH AGENT] Gathered findings for all subtasks")
    
    return {
        "literature_findings": all_findings,
        "current_step": "search_complete"
    }

def analysis_agent(state: ResearchState) -> dict:
    """
    Synthesizes all literature findings into a coherent analysis.
    Also identifies research gaps.
    """
    print(f"\n[ANALYSIS AGENT] Analyzing {len(state['literature_findings'])} sets of findings")
    
    findings_text = "\n\n".join(state["literature_findings"])
    
    prompt = f"""You are a research analysis expert. Synthesize these literature findings:

    Research Question: {state['research_question']}
    
    Literature Findings:
    {findings_text}
    
    Provide:
    1. A synthesis of the current state of knowledge (2-3 paragraphs)
    2. Key themes and patterns across the literature
    3. Identified research gaps and open questions
    4. Methodological considerations for future research
    
    Be specific and academic in tone."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    print(f"[ANALYSIS AGENT] Analysis complete")
    
    return {
        "analysis": response.content,
        "current_step": "analysis_complete"
    }

def writer_agent(state: ResearchState) -> dict:
    """
    Produces the final polished research summary report.
    """
    print(f"\n[WRITER AGENT] Writing final report")
    
    prompt = f"""You are an academic writer. Create a concise but comprehensive research summary.

    Research Question: {state['research_question']}
    
    Analysis: {state['analysis']}
    
    Write a structured research summary with these sections:
    ## Overview
    ## Key Findings
    ## Research Gaps
    ## Recommended Next Steps
    
    Keep it concise (400-600 words). Use academic language.
    This summary will be read by a PhD supervisor."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    print(f"[WRITER AGENT] Report complete")
    
    return {
        "final_report": response.content,
        "current_step": "report_complete"
    }

# ─── Build the Pipeline Graph ─────────────────────────────────────────────────
# This is a sequential pipeline (no loops for simplicity here)
# Each agent passes enriched state to the next

graph = StateGraph(ResearchState)

graph.add_node("planner", planner_agent)
graph.add_node("searcher", search_agent)
graph.add_node("analyzer", analysis_agent)
graph.add_node("writer", writer_agent)

# Linear pipeline: START → planner → searcher → analyzer → writer → END
graph.add_edge(START, "planner")
graph.add_edge("planner", "searcher")
graph.add_edge("searcher", "analyzer")
graph.add_edge("analyzer", "writer")
graph.add_edge("writer", END)

app = graph.compile()

# ─── Run the Research Pipeline ────────────────────────────────────────────────

research_question = """
What are the current approaches to reducing hallucinations in Large Language Models,
and what are the key open research challenges?
"""

print("=" * 65)
print("RESEARCH PIPELINE STARTING")
print("=" * 65)
print(f"Question: {research_question.strip()}")

result = app.invoke({
    "research_question": research_question,
    "subtasks": [],               # Start empty — planner will populate
    "literature_findings": [],    # Start empty — searcher will populate
    "analysis": "",
    "final_report": "",
    "current_step": "starting"
})

print("\n" + "=" * 65)
print("FINAL RESEARCH REPORT")
print("=" * 65)
print(result["final_report"])

# You can also inspect intermediate results
print("\n" + "=" * 65)
print(f"Subtasks planned: {len(result['subtasks'])}")
print(f"Literature sets found: {len(result['literature_findings'])}")
```

---

## 9. Debugging Tips

### Visualize Your Graph

LangGraph can generate a diagram of your graph. Install the dependency:

```bash
pip install pygraphviz  # or: pip install mermaid-py
```

Then in your code, after compiling:

```python
# Print a text representation of the graph
print(app.get_graph().draw_ascii())

# Or save as a PNG image (requires pygraphviz)
# from IPython.display import Image
# Image(app.get_graph().draw_mermaid_png())
```

### Streaming Output (See Every Step as It Happens)

Instead of waiting for the full result, stream events:

```python
# Stream all events from the graph
for event in app.stream({"messages": [HumanMessage(content="Hello")]}):
    for node_name, node_output in event.items():
        print(f"\n[NODE: {node_name}]")
        if "messages" in node_output:
            last_msg = node_output["messages"][-1]
            print(f"  {last_msg.content[:200]}")
```

### Add Verbose Print Statements

Add prints at the start of each node function — you already saw this in the examples with `[AGENT]`, `[TOOL]`, etc. This is the simplest and most effective debugging method.

### LangSmith (Optional — Advanced Observability)

LangSmith is a free observability platform by the same team. It records every LLM call, tool call, and state transition visually:

```bash
# Set these environment variables in your .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key  # from smith.langchain.com
LANGCHAIN_PROJECT=my_research_project
```

Once set, every time you run your graph, it automatically appears in the LangSmith UI at smith.langchain.com with full trace visualization.

---

## 10. Quick Reference Cheat Sheet

### Installation
```bash
pip install -U langgraph langchain langchain-openai python-dotenv
```

### Minimal Graph Template
```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    field1: str
    field2: int

def my_node(state: State) -> dict:
    return {"field1": "updated value"}

graph = StateGraph(State)
graph.add_node("my_node", my_node)
graph.add_edge(START, "my_node")
graph.add_edge("my_node", END)
app = graph.compile()

result = app.invoke({"field1": "hello", "field2": 42})
```

### Chatbot Template (with LLM)
```python
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END

llm = ChatOpenAI(model="gpt-4o-mini")

def chat(state: MessagesState) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}

graph = StateGraph(MessagesState)
graph.add_node("chat", chat)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)
app = graph.compile()
```

### Agent with Tools Template
```python
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

@tool
def my_tool(input: str) -> str:
    """Description LLM uses to decide when to call this."""
    return f"Result for: {input}"

tools = [my_tool]
llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

def agent(state: MessagesState) -> dict:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph = StateGraph(MessagesState)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
app = graph.compile()
```

### Key Concepts Summary

| Concept | What It Is | Example |
|---|---|---|
| `StateGraph` | The graph builder object | `graph = StateGraph(State)` |
| `State (TypedDict)` | Shared data between nodes | `class State(TypedDict): text: str` |
| `Node` | A Python function in the graph | `def my_node(state): return {...}` |
| `Normal Edge` | Always go from A to B | `graph.add_edge("A", "B")` |
| `Conditional Edge` | Go to A or B based on state | `graph.add_conditional_edges(...)` |
| `compile()` | Makes graph runnable | `app = graph.compile()` |
| `invoke()` | Run graph, wait for result | `result = app.invoke(initial_state)` |
| `stream()` | Run graph, get step-by-step | `for event in app.stream(...)` |
| `MessagesState` | Built-in state for chats | Manages message list automatically |
| `ToolNode` | Pre-built node that runs tools | `ToolNode([tool1, tool2])` |
| `tools_condition` | Routes to tools or END | Checks if last message has tool calls |
| `bind_tools()` | Tells LLM what tools exist | `llm.bind_tools([tool1, tool2])` |

### Common Mistakes to Avoid

1. **Forgetting `Annotated[List, add]` for list fields**: Without this, each node will overwrite the list instead of appending to it.

2. **Not calling `compile()` before `invoke()`**: The raw `StateGraph` object cannot be run directly.

3. **Returning the full state from a node**: Only return the fields that changed. LangGraph merges your return dict into the existing state.

4. **Missing `add_edge("last_node", END)`**: Without an edge to `END`, your graph will get stuck.

5. **Not binding tools to the LLM**: If you forget `llm.bind_tools(tools)`, the LLM won't know the tools exist and will never call them.

---

## Further Learning Resources

- **Official LangGraph Docs**: https://docs.langchain.com (search "LangGraph")
- **[LangGraph Install Guide](https://docs.langchain.com/oss/python/langgraph/install)** — Installation instructions
- **[LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview)** — Introduction to LangChain
- **[LangChain Quickstart](https://docs.langchain.com/oss/python/langchain/quickstart)** — Build your first agent
- **LangChain Tutorial**: See [README_LANGCHAIN.md](README_LANGCHAIN.md) for a beginner-friendly LangChain guide (models, prompts, chains, tools).
- **LangChain Academy** (free course): https://academy.langchain.com
- **GitHub Examples**: https://github.com/langchain-ai/langgraph/tree/main/examples
- **LangSmith (observability)**: https://smith.langchain.com

---

*Documentation created for PhD research use. All examples use LangGraph (latest 2025 release). OpenAI's `gpt-4o-mini` is used as the default LLM — it is fast and affordable. Any LangChain-compatible LLM (Claude, Gemini, Llama via Ollama) can be substituted with minimal code changes.*
