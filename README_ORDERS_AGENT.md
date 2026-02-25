# Orders Agent & Chatbot — Design

> **Custom agentic chatbot** that can **query** and **update** laptop orders using function tools, an LLM, and conversation memory.

**Files:** [`langgraph_examples/Orders Agent.ipynb`](langgraph_examples/Orders%20Agent.ipynb) | [`langgraph_examples/example9_orders_agent.py`](langgraph_examples/example9_orders_agent.py)

---

## Overview

The Orders Chatbot answers questions about laptop orders *and* performs actions (updates). It is backed by an **Orders Agent** that uses LangGraph to orchestrate an LLM with two function tools.

| Layer | Responsibility |
|-------|---------------|
| **Orders Chatbot** | User interface + conversation memory. Accepts natural-language queries and displays results. |
| **Orders Agent** | LangGraph graph that reasons about prompts, calls tools, and produces answers. |
| **Function Tools** | Python functions that read from and write to the orders database. |
| **Orders Database** | RDBMS storing all laptop orders (simplified as a Pandas DataFrame for this example). |

**Example query:** *"Show me the order details for ORD-7311"* — the chatbot routes this through the agent, which calls `get_order_details`, and returns a natural-language answer.

---

## Function Tools

| Tool | Type | Description |
|------|------|-------------|
| `get_order_details` | **Query** | Returns details for a specific order given an `order_id` (customer, laptop model, quantity, status, etc.) |
| `update_quantity` | **Action** | Updates the quantity of laptops in an order given an `order_id` and new quantity. Each order has one laptop type for simplicity. |

In a real-world application there would be many more tools for both querying (search by date, filter by status) and updating (cancel order, change shipping address). These two cover the core read/write pattern.

---

## Architecture Diagram

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 720" font-family="Segoe UI, Arial, sans-serif" font-size="13">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#555"/>
    </marker>
    <marker id="arr-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb"/>
    </marker>
    <marker id="arr-g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#16a34a"/>
    </marker>
    <filter id="sh" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.10"/>
    </filter>
  </defs>

  <!-- Title -->
  <text x="390" y="30" text-anchor="middle" font-size="17" font-weight="bold" fill="#1e293b">Orders Agent — Graph Design</text>

  <!-- ─── USER ─── -->
  <rect x="305" y="50" width="170" height="42" rx="21" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5" filter="url(#sh)"/>
  <text x="390" y="76" text-anchor="middle" font-weight="600" fill="#0c4a6e">User</text>
  <line x1="390" y1="92" x2="390" y2="130" stroke="#555" stroke-width="1.4" marker-end="url(#arr)"/>
  <text x="400" y="116" font-size="11" fill="#64748b">query</text>

  <!-- ─── CHATBOT ─── -->
  <rect x="200" y="134" width="380" height="52" rx="10" fill="#faf5ff" stroke="#9333ea" stroke-width="1.5" filter="url(#sh)"/>
  <text x="390" y="158" text-anchor="middle" font-weight="700" fill="#6b21a8" font-size="14">Orders Chatbot</text>
  <text x="390" y="175" text-anchor="middle" font-size="11" fill="#7e22ce">UI + Conversation Memory</text>
  <line x1="390" y1="186" x2="390" y2="222" stroke="#555" stroke-width="1.4" marker-end="url(#arr)"/>

  <!-- ─── AGENT GRAPH BOX ─── -->
  <rect x="50" y="226" width="680" height="310" rx="14" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="6 3" filter="url(#sh)"/>
  <text x="70" y="250" font-size="12" font-weight="700" fill="#475569">Orders Agent (LangGraph)</text>

  <!-- START -->
  <circle cx="130" cy="290" r="16" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2"/>
  <text x="130" y="294" text-anchor="middle" font-size="10" font-weight="700" fill="#334155">START</text>
  <line x1="146" y1="290" x2="210" y2="290" stroke="#555" stroke-width="1.3" marker-end="url(#arr)"/>

  <!-- Orders LLM node -->
  <rect x="214" y="264" width="240" height="54" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
  <text x="334" y="286" text-anchor="middle" font-weight="700" fill="#1e40af" font-size="13">Orders LLM</text>
  <text x="334" y="304" text-anchor="middle" font-size="10" fill="#3b82f6">Analyze prompt · Determine actions · Review results</text>

  <!-- Arrow: LLM → Conditional edge -->
  <line x1="454" y1="291" x2="510" y2="291" stroke="#2563eb" stroke-width="1.3" marker-end="url(#arr-b)"/>

  <!-- Conditional edge diamond -->
  <polygon points="540,270 570,291 540,312 510,291" fill="#fff7ed" stroke="#ea580c" stroke-width="1.3"/>
  <text x="540" y="295" text-anchor="middle" font-size="9" font-weight="700" fill="#c2410c">tool</text>
  <text x="540" y="305" text-anchor="middle" font-size="9" font-weight="700" fill="#c2410c">call?</text>

  <!-- YES: Conditional → Order Tools -->
  <line x1="540" y1="312" x2="540" y2="380" stroke="#ea580c" stroke-width="1.3" marker-end="url(#arr)"/>
  <text x="548" y="350" font-size="10" font-weight="600" fill="#ea580c">yes</text>

  <!-- Order Tools node -->
  <rect x="400" y="384" width="280" height="70" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="1.2"/>
  <text x="540" y="408" text-anchor="middle" font-weight="700" fill="#92400e" font-size="13">Order Tools</text>
  <text x="540" y="426" text-anchor="middle" font-size="10" fill="#a16207">get_order_details · update_quantity</text>
  <text x="540" y="440" text-anchor="middle" font-size="10" fill="#a16207">Execute tool, write results to state</text>

  <!-- Loop back: Tools → LLM -->
  <path d="M 400 420 Q 160 420 160 310 Q 160 291 214 291" stroke="#16a34a" stroke-width="1.3" fill="none" marker-end="url(#arr-g)"/>
  <text x="148" y="370" font-size="10" fill="#16a34a" transform="rotate(-90,148,370)">results in state</text>

  <!-- NO: Conditional → END -->
  <line x1="570" y1="291" x2="660" y2="291" stroke="#ea580c" stroke-width="1.3" marker-end="url(#arr)"/>
  <text x="612" y="283" font-size="10" font-weight="600" fill="#ea580c">no (final answer)</text>

  <!-- END -->
  <circle cx="680" cy="291" r="16" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2"/>
  <text x="680" y="295" text-anchor="middle" font-size="10" font-weight="700" fill="#334155">END</text>

  <!-- Agent State bar -->
  <rect x="100" y="480" width="580" height="40" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>
  <text x="390" y="504" text-anchor="middle" font-weight="600" fill="#065f46" font-size="12">Agent State — query, LLM output, tool params, tool results, final answer</text>

  <!-- Answer arrow back -->
  <line x1="350" y1="226" x2="350" y2="186" stroke="#555" stroke-width="1.2" stroke-dasharray="5 3" marker-end="url(#arr)"/>
  <text x="310" y="210" font-size="11" fill="#64748b">answer</text>
  <line x1="350" y1="134" x2="350" y2="92" stroke="#555" stroke-width="1.2" stroke-dasharray="5 3" marker-end="url(#arr)"/>

  <!-- ─── DATA SOURCE ─── -->
  <rect x="230" y="570" width="320" height="56" rx="8" fill="#fff" stroke="#94a3b8" stroke-width="1.2" filter="url(#sh)"/>
  <text x="390" y="594" text-anchor="middle" font-weight="600" fill="#334155">Orders Database (Pandas DataFrame)</text>
  <text x="390" y="612" text-anchor="middle" font-size="11" fill="#64748b">OrderID, Customer, Laptop, Quantity, Status</text>
  <line x1="540" y1="454" x2="540" y2="540" stroke="#555" stroke-width="1" stroke-dasharray="4 3"/>
  <line x1="540" y1="540" x2="390" y2="540" stroke="#555" stroke-width="1" stroke-dasharray="4 3"/>
  <line x1="390" y1="540" x2="390" y2="570" stroke="#555" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arr)"/>

  <!-- ─── LEGEND ─── -->
  <rect x="50" y="650" width="680" height="36" rx="6" fill="#f1f5f9"/>
  <circle cx="80" cy="668" r="6" fill="#dbeafe" stroke="#2563eb"/>
  <text x="92" y="672" font-size="11" fill="#475569">LLM node</text>
  <polygon points="180,662 192,668 180,674 168,668" fill="#fff7ed" stroke="#ea580c" stroke-width="1"/>
  <text x="198" y="672" font-size="11" fill="#475569">Conditional edge</text>
  <circle cx="310" cy="668" r="6" fill="#fef3c7" stroke="#d97706"/>
  <text x="322" y="672" font-size="11" fill="#475569">Tool node</text>
  <circle cx="400" cy="668" r="6" fill="#ecfdf5" stroke="#059669"/>
  <text x="412" y="672" font-size="11" fill="#475569">Agent State</text>
  <circle cx="500" cy="668" r="6" fill="#faf5ff" stroke="#9333ea"/>
  <text x="512" y="672" font-size="11" fill="#475569">Chatbot</text>
  <line x1="580" y1="668" x2="610" y2="668" stroke="#16a34a" stroke-width="1.3"/>
  <text x="616" y="672" font-size="11" fill="#475569">Loop back</text>
</svg>

---

## Graph Design — Step by Step

The graph implements the classic **ReAct loop** (Reason → Act → Observe → Repeat):

### 1. START → Orders LLM

The graph begins at the **Orders LLM** node. It reads the user query from the agent state and sends it to the LLM. The LLM analyzes the prompt and returns a list of actions — specifically, the **tool to call** and its **parameters**.

The Orders LLM node writes both the incoming query and the LLM output (tool name + parameters) to the **agent state**.

### 2. Conditional Edge — Is There a Tool Call?

A **conditional edge** checks the LLM output stored in the agent state:
- **If the next action is a tool call** → route control to the **Order Tools** node
- **If the final answer is ready** → route to **END**

### 3. Order Tools Node

The Order Tools node reads from the agent state:
- **Which tool** to execute (`get_order_details` or `update_quantity`)
- **Parameters** for the tool (e.g., `order_id`, `new_quantity`)

It executes the tool, fetches results, and **writes those results back to the agent state**.

### 4. Loop Back to Orders LLM

Control returns to the Orders LLM node. This time, it reads the **tool results** from the agent state and analyzes them:
- **If the LLM has sufficient information** → it generates the **final answer** and writes it to state
- **If more information is needed** → it determines the next tool call, and the loop repeats

### 5. END

When the conditional edge determines there are no more tool calls (the final answer is ready), the graph ends. The results in the agent state are passed back to the **Orders Chatbot**, which displays them to the user.

---

## Data Flow Through Agent State

All data is exchanged through the **agent state**, never through edges. Edges only transfer control.

```
┌──────────────────────────────────────────────────────────────────┐
│                        AGENT STATE                                │
│                                                                    │
│  messages:        [user query, LLM responses, tool results, ...]  │
│  tool_calls:      [{name: "get_order_details", args: {...}}]      │
│  tool_results:    "Order ORD-7311: 3x AlphaBook Pro, shipped"     │
│  final_answer:    "Order ORD-7311 contains 3 AlphaBook Pro..."    │
└──────────────────────────────────────────────────────────────────┘

  Node writes to state ──►  Next node reads from state
```

---

## Component Summary

| Component | Role | Implementation |
|-----------|------|----------------|
| **Orders Chatbot** | User interface + conversation memory | Accepts queries, maintains history, displays answers |
| **Orders Agent** | LangGraph graph orchestrating LLM + tools | `StateGraph` with LLM node, tool node, conditional edge |
| **Orders LLM node** | Analyzes prompts, determines actions, reviews tool results | LLM node — calls `llm.invoke(messages)` |
| **Order Tools node** | Executes `get_order_details` / `update_quantity` | Tool node — reads tool name + params from state |
| **Conditional edge** | Routes to tools (if tool call) or END (if done) | Equivalent to `tools_condition` in LangGraph |
| **Agent State** | Shared memory for all nodes | Stores query, LLM output, tool params, tool results, final answer |
| **Orders Database** | Stores laptop order data | Pandas DataFrame (simulating RDBMS) |

---

## Orders Data Schema

Each order contains one laptop type (simplified for this example):

| Column | Type | Description |
|--------|------|-------------|
| `OrderID` | str | Unique order identifier (e.g., `ORD-7311`) |
| `Customer` | str | Customer name |
| `Laptop` | str | Laptop model name |
| `Quantity` | int | Number of units ordered |
| `Status` | str | Order status (e.g., `Processing`, `Shipped`, `Delivered`) |

---

## Example Interactions

**Query (read):**
```
User: Show me the order details for ORD-7311
Agent: [calls get_order_details(order_id="ORD-7311")]
Agent: Order ORD-7311 is for 3 AlphaBook Pro laptops, currently in "Shipped" status.
```

**Query (update):**
```
User: Change the quantity for ORD-7311 to 5
Agent: [calls update_quantity(order_id="ORD-7311", new_quantity=5)]
Agent: Done — the quantity for order ORD-7311 has been updated to 5 units.
```

**Multi-step:**
```
User: What is the quantity for ORD-7311, and update it to 10
Agent: [calls get_order_details(order_id="ORD-7311")] → current quantity is 3
Agent: [calls update_quantity(order_id="ORD-7311", new_quantity=10)] → updated
Agent: Order ORD-7311 previously had 3 AlphaBook Pro units. I've updated it to 10.
```

---

## Prerequisites — API Key Setup

This example requires an LLM API key. Create a `.env` file in the project root:

```bash
# For OpenAI (default in our examples):
OPENAI_API_KEY=sk-your-key-here
```

The code loads this automatically with `load_dotenv()`. If you use a different LLM provider, adjust the import and model setup accordingly:

| Provider | Install | Import | Key Variable |
|----------|---------|--------|-------------|
| **OpenAI** | `pip install langchain-openai` | `from langchain_openai import ChatOpenAI` | `OPENAI_API_KEY` |
| **Azure OpenAI** | `pip install langchain-openai` | `from langchain_openai import AzureChatOpenAI` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| **Anthropic** | `pip install langchain-anthropic` | `from langchain_anthropic import ChatAnthropic` | `ANTHROPIC_API_KEY` |
| **Ollama (local, free)** | `pip install langchain-ollama` | `from langchain_ollama import ChatOllama` | No key needed |

> **Never commit `.env` to git.** Add it to `.gitignore`.

---

## LangGraph Concepts Used

This example demonstrates several core LangGraph concepts (see [README_COMPONENTS.md](README_COMPONENTS.md)):

| Concept | How It Appears |
|---------|---------------|
| **LLM node** | Orders LLM — integrates with the language model to analyze prompts and create actions |
| **Tool node** | Order Tools — executes the function tools and returns results |
| **Basic edge** | START → Orders LLM, Order Tools → Orders LLM |
| **Conditional edge** | After Orders LLM — checks if there's a tool call or if the job is finished |
| **Agent State** | Shared memory that nodes read/write; no data flows through edges |
| **START / END** | Entry and exit points of the graph |
| **`@tool` decorator** | `get_order_details` and `update_quantity` are Python functions turned into LLM-callable tools |
| **`bind_tools`** | LLM is made aware of the two tools so it can request them |

---

## Run

```bash
pip install pandas langchain-openai python-dotenv langgraph
python langgraph_examples/example9_orders_agent.py
```

Or open [`langgraph_examples/Orders Agent.ipynb`](langgraph_examples/Orders%20Agent.ipynb) and run the cells.
