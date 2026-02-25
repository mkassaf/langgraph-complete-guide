# Multi-Agent Router — Design

> **Multi-agent system** that uses the **routing pattern** to direct user queries to the appropriate specialized agent — a Product QnA Agent or an Orders Agent — while handling small talk directly.

**Files:** [`langgraph_examples/Multi-Agent Router.ipynb`](langgraph_examples/Multi-Agent%20Router.ipynb) | [`langgraph_examples/example11_multi_agent_router.py`](langgraph_examples/example11_multi_agent_router.py)

---

## Overview

Enterprise workflows are complex, requiring multiple systems and people to work together to achieve a goal. Creating specialized agents for specific tasks and getting them to work together helps achieve complex automation while improving efficiency. This example demonstrates the **multi-agent pattern** combined with the **routing pattern**.

| Layer | Responsibility |
|-------|---------------|
| **Router** | LLM-based classifier that inspects each user message and forwards it to the correct specialist or handles small talk directly. |
| **Product QnA Agent** | ReAct agent (from Example 8) that answers product feature and pricing questions using RAG + CSV tools. |
| **Orders Agent** | Custom StateGraph agent (from Example 9) that queries and updates laptop orders using function tools. |
| **Small Talk Node** | Handles greetings, farewells, and other non-domain queries with a friendly professional response. |

**Example query:** *"Tell me about the features of SpectraBook"* — the Router classifies this as PRODUCT and forwards it to the Product QnA Agent, which calls its RAG tool and returns a response.

---

## Why Multi-Agent Systems?

Why can't we build one single big agent for the same thing?

- **Separation of concerns**: Individual agents are built to handle a specific task or domain. A given workflow may need multiple tasks or multi-domain expertise.
- **Reusability**: A single agent can be part of multiple workflows. Each agent can be built in-house, acquired from open source, or from third parties.
- **Simplicity**: Following the multi-agent pattern allows building complex workflows from individual agent building blocks, leveraging existing best-of-breed agents and minimizing custom work.
- **Mimics human teams**: Individual agents collaborate and coordinate like a team of humans, each leveraging their expertise while taking help from others.

---

## The Routing Pattern

The routing pattern uses a classifier agent (the Router) to inspect each incoming query and decide which specialist should handle it. Unlike the supervisor pattern (Example 4), this is a **one-way routing** — the Router forwards to one specialist, which then routes directly to END. The Router does not loop or re-evaluate.

**Key characteristics:**
- **LLM-based classification**: The Router uses an LLM with a prompt that constrains output to one of four labels
- **One-way flow**: Each specialist handles the query and routes to END (no feedback loop to the Router)
- **Agent-as-node**: Sub-agents are wrapped with `functools.partial` so they can serve as graph nodes
- **Shared thread_id**: The Router passes the conversation thread_id to each sub-agent so they maintain their own memory

---

## What is `functools.partial`?

A key technique in this example is wrapping sub-agents as graph nodes using `functools.partial`. Understanding this standard-library function is essential.

`functools.partial` creates a **new function** from an existing one by pre-filling some of its arguments. The remaining arguments are supplied when the new function is called later.

```python
import functools

# Original function — takes 4 arguments
def agent_node(state, agent, name, config):
    result = agent.invoke(state, ...)
    return {"messages": [AIMessage(result["messages"][-1].content)]}

# Create a specialized version with `agent` and `name` already filled in
product_qna_node = functools.partial(
    agent_node, agent=product_qna_agent, name="Product_QnA_Agent"
)
```

Now `product_qna_node(state, config)` is equivalent to calling `agent_node(state, agent=product_qna_agent, name="Product_QnA_Agent", config)`.

**Why is this needed?** LangGraph node functions must accept `(state)` or `(state, config)`. But our `agent_node` helper needs extra arguments (`agent`, `name`) to know *which* sub-agent to invoke. `functools.partial` solves this by "baking in" those extra arguments ahead of time, producing a function with the right signature for LangGraph.

```python
# Without partial — LangGraph can't pass `agent` and `name`
router_graph.add_node("Product_Agent", agent_node)  # ✗ missing args

# With partial — `agent` and `name` are pre-filled
router_graph.add_node("Product_Agent", product_qna_node)  # ✓ works
```

This is a standard Python pattern for adapting functions with extra parameters into callbacks that expect a fixed signature.

---

## Architecture Diagram

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 700" font-family="Segoe UI, Arial, sans-serif" font-size="13">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#555"/>
    </marker>
    <marker id="arr-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb"/>
    </marker>
    <marker id="arr-o" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#ea580c"/>
    </marker>
    <filter id="sh" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.10"/>
    </filter>
  </defs>

  <!-- Title -->
  <text x="410" y="30" text-anchor="middle" font-size="17" font-weight="bold" fill="#1e293b">Multi-Agent Router — Graph Design</text>

  <!-- ─── USER ─── -->
  <rect x="325" y="50" width="170" height="42" rx="21" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5" filter="url(#sh)"/>
  <text x="410" y="76" text-anchor="middle" font-weight="600" fill="#0c4a6e">User</text>
  <line x1="410" y1="92" x2="410" y2="140" stroke="#555" stroke-width="1.4" marker-end="url(#arr)"/>
  <text x="420" y="120" font-size="11" fill="#64748b">query</text>

  <!-- ─── GRAPH BOX ─── -->
  <rect x="30" y="146" width="760" height="460" rx="14" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="6 3" filter="url(#sh)"/>
  <text x="50" y="172" font-size="12" font-weight="700" fill="#475569">Multi-Agent Router (LangGraph)</text>

  <!-- START -->
  <circle cx="110" cy="220" r="16" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2"/>
  <text x="110" y="224" text-anchor="middle" font-size="10" font-weight="700" fill="#334155">START</text>
  <line x1="126" y1="220" x2="215" y2="220" stroke="#555" stroke-width="1.3" marker-end="url(#arr)"/>

  <!-- Router LLM node -->
  <rect x="219" y="196" width="160" height="50" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
  <text x="299" y="216" text-anchor="middle" font-weight="700" fill="#1e40af" font-size="13">Router LLM</text>
  <text x="299" y="234" text-anchor="middle" font-size="10" fill="#3b82f6">Classify query</text>

  <!-- Arrow: Router → Conditional edge -->
  <line x1="379" y1="221" x2="445" y2="221" stroke="#2563eb" stroke-width="1.3" marker-end="url(#arr-b)"/>

  <!-- Conditional edge diamond -->
  <polygon points="480,198 515,221 480,244 445,221" fill="#fff7ed" stroke="#ea580c" stroke-width="1.3"/>
  <text x="480" y="218" text-anchor="middle" font-size="8" font-weight="700" fill="#c2410c">find</text>
  <text x="480" y="230" text-anchor="middle" font-size="8" font-weight="700" fill="#c2410c">route</text>

  <!-- PRODUCT branch -->
  <line x1="480" y1="198" x2="480" y2="160" stroke="#ea580c" stroke-width="1.3"/>
  <line x1="480" y1="160" x2="620" y2="160" stroke="#ea580c" stroke-width="1.3" marker-end="url(#arr-o)"/>
  <text x="540" y="152" font-size="10" font-weight="600" fill="#ea580c">PRODUCT</text>

  <!-- Product Agent node -->
  <rect x="624" y="136" width="150" height="50" rx="8" fill="#dcfce7" stroke="#16a34a" stroke-width="1.2"/>
  <text x="699" y="156" text-anchor="middle" font-weight="700" fill="#166534" font-size="12">Product Agent</text>
  <text x="699" y="174" text-anchor="middle" font-size="9" fill="#15803d">RAG + Pricing tools</text>

  <!-- ORDER branch -->
  <line x1="515" y1="221" x2="620" y2="221" stroke="#ea580c" stroke-width="1.3" marker-end="url(#arr-o)"/>
  <text x="560" y="213" font-size="10" font-weight="600" fill="#ea580c">ORDER</text>

  <!-- Orders Agent node -->
  <rect x="624" y="196" width="150" height="50" rx="8" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.2"/>
  <text x="699" y="216" text-anchor="middle" font-weight="700" fill="#854d0e" font-size="12">Orders Agent</text>
  <text x="699" y="234" text-anchor="middle" font-size="9" fill="#a16207">Query + Update tools</text>

  <!-- SMALLTALK branch -->
  <line x1="480" y1="244" x2="480" y2="290" stroke="#ea580c" stroke-width="1.3"/>
  <line x1="480" y1="290" x2="620" y2="290" stroke="#ea580c" stroke-width="1.3" marker-end="url(#arr-o)"/>
  <text x="535" y="282" font-size="10" font-weight="600" fill="#ea580c">SMALLTALK</text>

  <!-- Small Talk node -->
  <rect x="624" y="266" width="150" height="50" rx="8" fill="#faf5ff" stroke="#9333ea" stroke-width="1.2"/>
  <text x="699" y="286" text-anchor="middle" font-weight="700" fill="#6b21a8" font-size="12">Small Talk</text>
  <text x="699" y="304" text-anchor="middle" font-size="9" fill="#7e22ce">Greetings & farewells</text>

  <!-- END node (right) -->
  <circle cx="699" cy="380" r="16" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2"/>
  <text x="699" y="384" text-anchor="middle" font-size="10" font-weight="700" fill="#334155">END</text>

  <!-- Edges to END from each agent -->
  <line x1="699" y1="186" x2="699" y2="364" stroke="#555" stroke-width="1" marker-end="url(#arr)"/>
  <line x1="699" y1="246" x2="699" y2="364" stroke="#555" stroke-width="1"/>
  <line x1="699" y1="316" x2="699" y2="364" stroke="#555" stroke-width="1"/>

  <!-- END fallback branch (from diamond) -->
  <line x1="480" y1="244" x2="480" y2="370" stroke="#ea580c" stroke-width="1" stroke-dasharray="4 3"/>
  <text x="440" y="330" font-size="10" font-weight="600" fill="#ea580c">END</text>
  <circle cx="480" cy="380" r="12" fill="#e2e8f0" stroke="#64748b" stroke-width="1"/>
  <text x="480" y="384" text-anchor="middle" font-size="8" font-weight="700" fill="#334155">END</text>

  <!-- Agent State bar -->
  <rect x="80" y="430" width="660" height="40" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>
  <text x="410" y="454" text-anchor="middle" font-weight="600" fill="#065f46" font-size="12">Agent State — messages: [user query, router classification, agent response]</text>

  <!-- Sub-agent detail boxes -->
  <rect x="80" y="490" width="300" height="95" rx="6" fill="#f0fdf4" stroke="#16a34a" stroke-width="1"/>
  <text x="230" y="510" text-anchor="middle" font-weight="600" fill="#166534" font-size="11">Product QnA Agent (Example 8)</text>
  <text x="230" y="528" text-anchor="middle" font-size="10" fill="#15803d">create_react_agent + MemorySaver</text>
  <text x="230" y="546" text-anchor="middle" font-size="10" fill="#15803d">Tools: get_laptop_price, get_product_features</text>
  <text x="230" y="564" text-anchor="middle" font-size="10" fill="#15803d">Data: laptop_pricing.csv + RAG descriptions</text>

  <rect x="420" y="490" width="300" height="95" rx="6" fill="#fefce8" stroke="#ca8a04" stroke-width="1"/>
  <text x="570" y="510" text-anchor="middle" font-weight="600" fill="#854d0e" font-size="11">Orders Agent (Example 9)</text>
  <text x="570" y="528" text-anchor="middle" font-size="10" fill="#a16207">Custom StateGraph + MemorySaver</text>
  <text x="570" y="546" text-anchor="middle" font-size="10" fill="#a16207">Tools: get_order_details, update_quantity</text>
  <text x="570" y="564" text-anchor="middle" font-size="10" fill="#a16207">Data: laptop_orders.csv (Pandas DataFrame)</text>

  <!-- ─── LEGEND ─── -->
  <rect x="30" y="620" width="760" height="36" rx="6" fill="#f1f5f9"/>
  <circle cx="60" cy="638" r="6" fill="#dbeafe" stroke="#2563eb"/>
  <text x="72" y="642" font-size="11" fill="#475569">Router</text>
  <polygon points="140,632 152,638 140,644 128,638" fill="#fff7ed" stroke="#ea580c" stroke-width="1"/>
  <text x="158" y="642" font-size="11" fill="#475569">Conditional edge</text>
  <circle cx="280" cy="638" r="6" fill="#dcfce7" stroke="#16a34a"/>
  <text x="292" y="642" font-size="11" fill="#475569">Product Agent</text>
  <circle cx="400" cy="638" r="6" fill="#fef9c3" stroke="#ca8a04"/>
  <text x="412" y="642" font-size="11" fill="#475569">Orders Agent</text>
  <circle cx="510" cy="638" r="6" fill="#faf5ff" stroke="#9333ea"/>
  <text x="522" y="642" font-size="11" fill="#475569">Small Talk</text>
  <circle cx="600" cy="638" r="6" fill="#ecfdf5" stroke="#059669"/>
  <text x="612" y="642" font-size="11" fill="#475569">Agent State</text>
</svg>

---

## Graph Design — Step by Step

### 1. START → Router LLM

The graph begins at the **Router LLM** node. It reads the user's query, prepends a system prompt that constrains the output to one of four labels (PRODUCT, ORDER, SMALLTALK, END), and invokes the LLM. The LLM returns a single-word classification.

### 2. Conditional Edge — find_route

A **conditional edge** reads the Router's classification from the last message and routes to the corresponding node:
- **PRODUCT** → Product Agent node
- **ORDER** → Orders Agent node
- **SMALLTALK** → Small Talk node
- **END** → graph END (fallback)

### 3. Specialist Nodes

Each specialist handles the query independently with its own tools and memory:

- **Product Agent**: A prebuilt ReAct agent (`create_react_agent`) with RAG retrieval for features and CSV lookup for pricing. Uses its own `MemorySaver` so "How much does it cost?" remembers the last laptop discussed.

- **Orders Agent**: A custom `StateGraph` agent with `get_order_details` (READ) and `update_quantity` (WRITE) tools. Uses its own `MemorySaver` so "add one more" remembers the current order.

- **Small Talk**: A simple LLM node with a professional greeting/farewell prompt. No tools needed.

### 4. One-Way Flow → END

After any specialist handles the query, control flows directly to END. The Router does not re-evaluate — this is a one-way routing pattern, not a supervisor loop.

---

## Data Flow Through Agent State

```
┌──────────────────────────────────────────────────────────────────┐
│                        ROUTER AGENT STATE                         │
│                                                                    │
│  messages:                                                         │
│    [0] HumanMessage  — "Tell me about SpectraBook features"        │
│    [1] AIMessage     — "PRODUCT"  (Router classification)          │
│    [2] AIMessage     — "The SpectraBook S features..."  (agent)    │
└──────────────────────────────────────────────────────────────────┘

  Router classifies ──► Conditional edge routes ──► Specialist responds
```

Each sub-agent maintains its own internal state (via its own `MemorySaver`), while the Router graph only sees the final response.

---

## Routing vs. Supervisor Pattern

| Aspect | Routing (this example) | Supervisor (Example 4) |
|--------|----------------------|----------------------|
| **Flow** | One-way: Router → Specialist → END | Loop: Supervisor → Specialist → Supervisor → ... → FINISH |
| **Re-evaluation** | No — Router classifies once | Yes — Supervisor can call multiple specialists |
| **Multi-step** | One specialist per query | Multiple specialists per query |
| **Complexity** | Simpler | More complex |
| **Best for** | Clear single-domain queries | Multi-part queries needing multiple domains |

---

## Component Summary

| Component | Role | Implementation |
|-----------|------|----------------|
| **Router LLM** | Classifies queries into PRODUCT / ORDER / SMALLTALK / END | LLM node with constrained output prompt |
| **Conditional edge** | Routes to the appropriate specialist | `find_route` reads the Router's classification |
| **Product Agent** | Answers product feature and pricing questions | `create_react_agent` with RAG + pricing tools |
| **Orders Agent** | Queries and updates laptop orders | Custom `StateGraph` with query + update tools |
| **Small Talk** | Handles greetings and farewells | LLM node with a professional prompt |
| **Agent-as-node** | Wraps sub-agents as graph nodes | `functools.partial(agent_node, agent=..., name=...)` |
| **Router Agent State** | Shared memory for router graph | Stores query, classification, and final response |

---

## Example Interactions

**Product query:**
```
User: Tell me about the features of SpectraBook
Router: PRODUCT
Product Agent: The SpectraBook S features an Intel Core i9, 64GB RAM, 2TB SSD...
```

**Order query:**
```
User: What is the status of order ORD-7311?
Router: ORDER
Orders Agent: Order ORD-7311: NanoEdge Flex, Quantity 2, Delivery 2024-10-19
```

**Multi-turn conversation (cross-domain):**
```
User: How are you doing?
Agent: Hello! I can help with laptop product features and order management.

User: Please show me the details of the order ORD-7311
Agent: Order ORD-7311: NanoEdge Flex, Quantity 2, Delivery 2024-10-19

User: Can you add one more of that laptop to the order?
Agent: Updated! Order ORD-7311 now has 3 NanoEdge Flex laptops.

User: Tell me about the features of SpectraBook laptop
Agent: The SpectraBook S features an Intel Core i9, 64GB RAM, 2TB SSD...

User: How much does it cost?
Agent: The SpectraBook S is priced at $2,499.

User: Bye
Agent: Thank you for reaching out! Have a great day!
```

---

## Prerequisites

This example requires the same dependencies as Examples 8 and 9:

```bash
pip install pandas langchain-openai langchain-community langchain-chroma langchain-text-splitters python-dotenv langgraph
```

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-your-key-here
```

**Data files:**
- `data/laptop_pricing.csv` — Product names and prices
- `data/laptop_descriptions.txt` — Product feature descriptions (for RAG)
- `data/laptop_orders.csv` — Order records (Order ID, Product, Quantity, Date)

---

## LangGraph Concepts Used

| Concept | How It Appears |
|---------|---------------|
| **Multi-agent composition** | Two independent agents composed as nodes in a larger router graph |
| **Routing pattern** | LLM classifies queries and forwards to the correct specialist |
| **Agent-as-node** | `functools.partial` wraps sub-agent invocation for use as a graph node |
| **Conditional edge** | `find_route` reads the Router's output and routes accordingly |
| **Basic edge** | Each specialist → END (one-way flow) |
| **Agent State** | Router graph state stores messages; sub-agents have their own internal state |
| **MemorySaver** | Each sub-agent has its own checkpointer for conversation memory |
| **`create_react_agent`** | Product QnA Agent uses the prebuilt ReAct agent |
| **Custom StateGraph** | Orders Agent uses a manually-wired ReAct loop |
| **`@tool` decorator** | Four tools across two agents (pricing, features, order details, update) |

---

## Run

```bash
pip install pandas langchain-openai langchain-community langchain-chroma langchain-text-splitters python-dotenv langgraph
python langgraph_examples/example11_multi_agent_router.py
```

Or open [`langgraph_examples/Multi-Agent Router.ipynb`](langgraph_examples/Multi-Agent%20Router.ipynb) and run the cells.
