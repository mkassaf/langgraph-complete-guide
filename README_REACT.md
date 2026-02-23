# ReAct: Reasoning + Acting for AI Agents

> **Who this is for:** Beginners learning how AI agents use tools. No prior agent experience needed.
> **Goal:** Understand the ReAct pattern and run three working examples.

**References:** [LangChain Agents docs](https://docs.langchain.com/oss/python/langchain/agents) | [Example 3 in main README](README.md#6-example-3-agent-with-tools-react-pattern)

**Prerequisites:** Python basics ([README_PREREQUISITES.md](README_PREREQUISITES.md)), LangChain intro ([README_LANGCHAIN.md](README_LANGCHAIN.md) for tools), and `.env` with `OPENAI_API_KEY`.

---

## Table of Contents

1. [What is ReAct?](#1-what-is-react)
2. [Why Do Agents Need Tools?](#2-why-do-agents-need-tools)
3. [The ReAct Loop](#3-the-react-loop)
4. [Example 1: Math + Research Agent](#4-example-1-math--research-agent)
5. [Example 2: Weather + Calculator Agent](#5-example-2-weather--calculator-agent)
6. [Example 3: Minimal Math Agent (find_sum + find_product)](#6-example-3-minimal-math-agent)
7. [Key Concepts Cheat Sheet](#7-key-concepts-cheat-sheet)

---

## 1. What is ReAct?

**ReAct** stands for **Reasoning + Acting**. It's the most common pattern for AI agents that use tools.

An agent is an LLM (like GPT-4) that can:
- **Reason** — Think about what to do
- **Act** — Call a tool (calculator, search, API)
- **Observe** — See the tool's result
- **Reason again** — Decide: call another tool or give a final answer

The agent repeats this loop until it has enough information to answer the user.

---

## 2. Why Do Agents Need Tools?

LLMs are powerful at language but weak at:

| Task | Why LLMs Struggle | Tool Solution |
|------|-------------------|---------------|
| Math | Can make arithmetic errors | `calculate` tool |
| Current data | Training cutoff; no live access | `search` or `get_weather` tool |
| External APIs | Can't call APIs directly | Custom tools |

**Tools** are Python functions the LLM can call. When you use `@tool`, LangChain turns the function into a schema (name, description, parameters) that gets sent to the LLM. The LLM reads each tool's **docstring** and **parameter types** to decide when and how to use it. That's why clear docstrings matter!

---

## 3. The ReAct Loop

From the [LangChain Agents documentation](https://docs.langchain.com/oss/python/langchain/agents):

```
User Query → LLM (Reason) → [Tool Call?] → Tools (Act) → Observation → LLM (Reason) → ... → Final Answer
```

**Flow:**
1. User asks: "What is 127 × 34?"
2. **Reason:** LLM thinks: "I need to multiply. I have a multiply_numbers tool."
3. **Act:** LLM returns a tool call: `multiply_numbers(127, 34)`
4. **Observe:** Tool returns `4318`
5. **Reason:** LLM thinks: "I have the answer. I can respond."
6. **Finish:** LLM returns: "127 × 34 = 4,318"

**Example of a multi-step ReAct loop** (from LangChain docs):

- **Prompt:** "Find the most popular wireless headphones and check if they're in stock"
- **Reason:** "I need to search for products."
- **Act:** Call `search_products("wireless headphones")`
- **Observe:** "Top result: WH-1000XM5"
- **Reason:** "I need to check inventory for the top result."
- **Act:** Call `check_inventory("WH-1000XM5")`
- **Observe:** "10 units in stock"
- **Reason:** "I have everything. I can answer."
- **Finish:** "The most popular model is WH-1000XM5 with 10 units in stock."

---

## 4. Example 1: Math + Research Agent

**Location:** [`langgraph_examples/example3_agent_with_tools.py`](langgraph_examples/example3_agent_with_tools.py)

**Tools:**
- `add_numbers(a, b)` — Addition
- `multiply_numbers(a, b)` — Multiplication
- `get_paper_info(paper_title)` — Look up research papers (mock)

**Run:**
```bash
python langgraph_examples/example3_agent_with_tools.py
```

**Sample queries:**
- "What is 127 multiplied by 34?"
- "Tell me about the paper 'Attention is All You Need'"
- "What is 15.5 + 27.3? And summarize BERT."

**Graph structure:**
```
START → agent → [tools_condition] → tools (if tool_calls) OR END (if done)
                      ↑                    |
                      └────────────────────┘
```

The agent loops: Agent → Tools → Agent → ... until it responds with plain text (no more tool calls).

---

## 5. Example 2: Weather + Calculator Agent

**Location:** [`langgraph_examples/ReAct Agent in LangGraph.ipynb`](langgraph_examples/ReAct%20Agent%20in%20LangGraph.ipynb) (Example 2 section)

**Tools:**
- `get_weather(city)` — Get weather for a city (mock)
- `add(a, b)` — Add two numbers

**Sample queries:**
- "What's the weather in Paris?"
- "What's the weather in Tokyo and what is 10 + 20?"
- "Add 5 and 7, then tell me the weather in London"

This example shows an agent that combines different tool types (weather + math) in one response. Run the notebook cells to try it.

---

## 6. Example 3: Minimal Math Agent (find_sum + find_product)

**Location:** [`langgraph_examples/example6_react_math_agent.py`](langgraph_examples/example6_react_math_agent.py)

**Tools:**
- `find_sum(x, y)` — Add two integers
- `find_product(x, y)` — Multiply two integers

**Run:**
```bash
python langgraph_examples/example6_react_math_agent.py
```

**Key idea:** The system prompt says *"Solve by using ONLY the tools available. Do NOT solve the problem yourself"* — so the agent must call tools instead of computing in its head. This makes the ReAct loop visible: every math question triggers a tool call.

**Sample queries:**
- "What is the sum of 2 and 3?" → Agent calls `find_sum(2, 3)` → Returns "5"
- "What is 3 multiplied by 2 and 5 + 1?" → Agent can call **both** `find_product(3, 2)` and `find_sum(5, 1)` in one turn (parallel tool calls)

**Step-by-step output:** The script prints each message (HumanMessage → AIMessage with tool_calls → ToolMessage → AIMessage with final answer), similar to `debug=True` in `create_react_agent`.

---

## 7. Key Concepts Cheat Sheet

| Concept | What It Is |
|---------|------------|
| **ReAct** | Reason → Act → Observe → Reason → ... → Answer |
| **Tool** | A Python function with `@tool`. The LLM uses the docstring to decide when to call it. |
| **bind_tools** | `llm.bind_tools(tools)` — Injects tool schemas into the LLM's context so it knows what it can call. |
| **tool_calls** | When the LLM wants to use a tool, it returns an `AIMessage` with `tool_calls` (structured JSON) instead of `content`. |
| **ToolNode** | Pre-built LangGraph node that executes `tool_calls` and returns `ToolMessage` results. |
| **tools_condition** | Router: if last message has `tool_calls` → go to tools; else → END. |

**Docstrings matter!** The LLM reads them to decide which tool to use. Write clear, action-oriented descriptions:
```python
@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together. Use this for any multiplication."""
    return a * b
```

---

## Next Steps

- **Main tutorial:** [README.md](README.md) — Full LangGraph guide
- **LangChain basics:** [README_LANGCHAIN.md](README_LANGCHAIN.md) — Models, prompts, chains, tools
- **Python basics:** [README_PREREQUISITES.md](README_PREREQUISITES.md) — If you're new to Python
