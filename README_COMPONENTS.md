# LangGraph & LangChain Components Reference

> **Purpose:** A glossary of the main classes and components used in this guide. Use this when you see a type or import and want to understand what it does.

**See also:** [Main README](README.md) | [ReAct Pattern](README_REACT.md) | [LangChain Tutorial](README_LANGCHAIN.md)

---

## Table of Contents

1. [State & Graph (LangGraph)](#1-state--graph-langgraph)
2. [Message Types (LangChain)](#2-message-types-langchain)
3. [Pre-built Nodes & Routers (LangGraph)](#3-pre-built-nodes--routers-langgraph)
4. [Tools (LangChain)](#4-tools-langchain)
5. [Graph Building](#5-graph-building)

---

## 1. State & Graph (LangGraph)

### `StateGraph`

**Import:** `from langgraph.graph import StateGraph`

**What it is:** The main builder object for defining a LangGraph workflow. You create a graph by specifying a state schema, adding nodes (functions), and connecting them with edges.

**Usage:**
```python
graph = StateGraph(State)   # State is a TypedDict or MessagesState
graph.add_node("name", my_function)
graph.add_edge(START, "name")
graph.add_edge("name", END)
app = graph.compile()      # Compile into a runnable app
result = app.invoke({"field": "value"})
```

**Key idea:** A `StateGraph` is a *definition* — it describes the workflow. You must call `.compile()` to get a runnable app.

---

### `MessagesState`

**Import:** `from langgraph.graph import MessagesState`

**What it is:** A built-in state type for chat/conversation workflows. It has a single field `messages` that holds a list of messages (HumanMessage, AIMessage, etc.).

**Under the hood (simplified):**
```python
# Roughly equivalent to:
class MessagesState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

The `add_messages` annotation is critical: it tells LangGraph to **append** new messages to the list instead of replacing it. Without this, each node would overwrite the entire conversation history.

**Usage:**
```python
graph = StateGraph(MessagesState)

def chat_node(state: MessagesState) -> dict:
    # state["messages"] = [HumanMessage(...), AIMessage(...), ...]
    response = llm.invoke(state["messages"])
    return {"messages": [response]}  # Appended, not replaced
```

**When to use:** Any chatbot, agent, or multi-turn conversation. Use a custom `TypedDict` when you have non-message state (e.g., `text`, `metadata`).

---

### `TypedDict` (Python standard library)

**Import:** `from typing import TypedDict`

**What it is:** A way to define a dictionary with fixed keys and value types. LangGraph uses it as the schema for state.

**Usage:**
```python
class State(TypedDict):
    text: str
    count: int

def node_a(state: State) -> dict:
    return {"text": state["text"] + " A"}  # Only update fields you change
```

**Key idea:** Each node returns a *partial* update (a dict with only the fields it changed). LangGraph merges this into the existing state.

---

### `START` and `END`

**Import:** `from langgraph.graph import START, END`

**What they are:** Special constants representing the entry and exit points of the graph.

- **START** — The virtual node before any real node. Use it in `add_edge(START, "first_node")`.
- **END** — The virtual node after the graph finishes. Use it in `add_edge("last_node", END)`.

**Usage:**
```python
graph.add_edge(START, "node_a")   # Graph begins at node_a
graph.add_edge("node_c", END)    # Graph ends after node_c
```

---

## 2. Message Types (LangChain)

All message types live in `langchain_core.messages`. Chat APIs use three roles: **system**, **user**, and **assistant**. These types map to those roles.

### `HumanMessage`

**Import:** `from langchain_core.messages import HumanMessage`

**What it is:** Represents a message from the **user**. Maps to the `user` role in the OpenAI/Anthropic API.

**Usage:**
```python
msg = HumanMessage(content="What is 2 + 2?")
# Or with tuples (common in LangGraph): ("user", "What is 2 + 2?")
```

---

### `SystemMessage`

**Import:** `from langchain_core.messages import SystemMessage`

**What it is:** Represents **instructions** for the assistant — personality, rules, format. Maps to the `system` role. The model sees this before the conversation.

**Usage:**
```python
system_msg = SystemMessage(content="""
You are a helpful research assistant.
Be concise and cite sources when uncertain.
""")
all_messages = [system_msg] + state["messages"]
response = llm.invoke(all_messages)
```

**Key idea:** The system message is usually prepended once at the start of the message list. It shapes *how* the model responds, not *what* it responds to.

---

### `AIMessage`

**Import:** `from langchain_core.messages import AIMessage`

**What it is:** Represents a message from the **assistant** (the LLM). Maps to the `assistant` role.

**Two forms:**
1. **Plain text response:** `AIMessage(content="The answer is 4.")`
2. **Tool call:** `AIMessage(content="", tool_calls=[{...}])` — when the LLM wants to call a tool, it returns an AIMessage with `tool_calls` instead of `content`.

**Usage:**
```python
# You typically don't create AIMessage manually — the LLM returns it
response = llm.invoke(messages)  # response is an AIMessage
```

---

### `ToolMessage`

**Import:** `from langchain_core.messages import ToolMessage`

**What it is:** The result of a tool execution. Sent back to the LLM so it can "observe" what the tool returned.

**Structure:**
- `content` — The tool's return value (e.g., `"5"` or `"72°F"`)
- `name` — The tool that was called (e.g., `"find_sum"`)
- `tool_call_id` — Links this message to the specific `tool_call` in the AIMessage

**Usage:** You rarely create `ToolMessage` manually — `ToolNode` does it for you when it executes tool calls.

---

## 3. Pre-built Nodes & Routers (LangGraph)

### `ToolNode`

**Import:** `from langgraph.prebuilt import ToolNode`

**What it is:** A pre-built node that executes tool calls from the last message. If the last message is an `AIMessage` with `tool_calls`, it runs each tool and returns `ToolMessage` results.

**Usage:**
```python
tools = [add_numbers, multiply_numbers]
graph.add_node("tools", ToolNode(tools))
```

**Flow:** Agent returns `AIMessage(tool_calls=[...])` → ToolNode runs each tool → Appends `ToolMessage` results to state → Graph routes back to agent (or elsewhere).

---

### `tools_condition`

**Import:** `from langgraph.prebuilt import tools_condition`

**What it is:** A routing function used with `add_conditional_edges`. It checks the last message: if it has `tool_calls`, route to `"tools"`; otherwise route to `END`.

**Usage:**
```python
graph.add_conditional_edges("agent", tools_condition)
# If last message has tool_calls → go to "tools"
# Else → go to END
```

**Typical pattern:** In a ReAct agent, the agent node either returns a final answer (no tool_calls) or requests tools (has tool_calls). `tools_condition` routes accordingly.

---

## 4. Tools (LangChain)

### `@tool` decorator

**Import:** `from langchain_core.tools import tool`

**What it is:** A decorator that turns a Python function into a LangChain tool. The LLM receives a schema (name, description, parameters) derived from the function's signature and docstring.

**Usage:**
```python
@tool
def find_sum(x: int, y: int) -> int:
    """Add two numbers. Use for any addition question."""
    return x + y
```

**Key idea:** The **docstring** is critical. The LLM reads it to decide *when* to call the tool and *what* it does. Write clear, action-oriented descriptions.

---

### `llm.bind_tools(tools)`

**What it is:** A method on chat models that injects tool schemas into the LLM's context. After binding, the model "knows" what tools exist and can return `tool_calls` instead of plain text.

**Usage:**
```python
tools = [find_sum, find_product]
llm_with_tools = llm.bind_tools(tools)
response = llm_with_tools.invoke(messages)
# response may have response.tool_calls = [{"name": "find_sum", "args": {"x": 2, "y": 3}}]
```

**Without `bind_tools`:** The LLM would never call tools — it wouldn't know they exist.

---

## 5. Graph Building

### `add_node(name, func)`

**What it does:** Registers a function as a node in the graph. The function must accept `state` and return a dict of updates.

```python
graph.add_node("chatbot", chatbot_node)
```

---

### `add_edge(source, target)`

**What it does:** Adds a fixed transition from one node to another. The graph always follows this edge.

```python
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")
graph.add_edge("node_b", END)
```

---

### `add_conditional_edges(source, condition, path_map)`

**What it does:** Adds a conditional transition. A function inspects the state and returns which node to go to next.

```python
# tools_condition returns "tools" or "__end__" based on last message
graph.add_conditional_edges("agent", tools_condition)
```

For custom routing:
```python
def my_router(state):
    if state["count"] > 5:
        return "node_b"
    return "node_a"

graph.add_conditional_edges("start", my_router)
# Router returns the next node name directly
```

---

### `compile()`

**What it does:** Compiles the graph definition into a runnable application. Returns an object with `.invoke()` and `.stream()`.

```python
app = graph.compile()
result = app.invoke(initial_state)
```

---

### `invoke(initial_state)` and `stream(initial_state)`

**What they do:**
- **`invoke`** — Runs the graph from START to END (or until no more edges). Returns the final state.
- **`stream`** — Same run, but yields events/chunks as they happen. Useful for debugging or streaming responses to a UI.

```python
result = app.invoke({"messages": [HumanMessage(content="Hello")]})
# result["messages"] contains the full conversation including the AI reply
```

---

## Quick Reference Table

| Component | Package | Purpose |
|-----------|---------|---------|
| `StateGraph` | langgraph.graph | Graph builder; defines workflow structure |
| `MessagesState` | langgraph.graph | Built-in state for message lists (append semantics) |
| `START` / `END` | langgraph.graph | Virtual entry/exit nodes |
| `HumanMessage` | langchain_core.messages | User message |
| `SystemMessage` | langchain_core.messages | System instructions for the model |
| `AIMessage` | langchain_core.messages | Assistant message (text or tool_calls) |
| `ToolMessage` | langchain_core.messages | Tool execution result |
| `ToolNode` | langgraph.prebuilt | Executes tool_calls from last message |
| `tools_condition` | langgraph.prebuilt | Routes to tools or END based on tool_calls |
| `@tool` | langchain_core.tools | Turns a function into a callable tool |
| `bind_tools` | Chat model method | Injects tool schemas into LLM context |
