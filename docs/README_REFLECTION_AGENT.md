# Reflection-Based Summary Agent — Design

> **Summarizer chatbot** that uses the **reflection pattern** to iteratively improve a summary of an input document through a generate → review → revise loop.

**Files:** [`langgraph_examples/Reflection Agent.ipynb`](../langgraph_examples/Reflection%20Agent.ipynb) | [`langgraph_examples/example10_reflection_agent.py`](../langgraph_examples/example10_reflection_agent.py)

---

## Overview

The Reflection Summary Chatbot takes an input body of text and returns a refined summary. Unlike our earlier examples that used tool-use and planning patterns, this example uses the **reflection pattern** — two LLM nodes (a summarizer and a reviewer) iteratively improve the output without any external tools.

| Layer | Responsibility |
|-------|---------------|
| **Summary Chatbot** | User interface + conversation memory. Accepts documents or follow-up instructions and displays the refined summary. |
| **Summarizer Node** | LLM node that generates or revises a summary of the input document. |
| **Reviewer Node** | LLM node that critiques the summary and provides improvement recommendations. |
| **Conditional Edge** | `should_continue` — checks if the maximum number of reflection iterations has been reached. |

**Example query:** *"Summarize the following text: [EcoSprint specification document]"* — the chatbot runs the reflection loop (summarize → review → revise × N) and returns a polished summary.

---

## The Reflection Pattern

The reflection pattern is a self-improvement loop where one LLM generates output and another LLM critiques it. The critique is fed back to the generator, which produces a revised version. This cycle repeats for a fixed number of iterations, progressively improving the quality.

**Key characteristics:**
- **No tools needed** — Both nodes are LLM calls with different system prompts
- **Self-improving** — Each iteration incorporates reviewer feedback
- **Bounded** — A conditional edge caps iterations to prevent infinite loops
- **Versatile** — Works for summarization, writing, code generation, or any task where quality can be reviewed

---

## Architecture Diagram

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 640" font-family="Segoe UI, Arial, sans-serif" font-size="13">
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
  <text x="390" y="30" text-anchor="middle" font-size="17" font-weight="bold" fill="#1e293b">Reflection Agent — Graph Design</text>

  <!-- ─── USER ─── -->
  <rect x="305" y="50" width="170" height="42" rx="21" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5" filter="url(#sh)"/>
  <text x="390" y="76" text-anchor="middle" font-weight="600" fill="#0c4a6e">User</text>
  <line x1="390" y1="92" x2="390" y2="130" stroke="#555" stroke-width="1.4" marker-end="url(#arr)"/>
  <text x="400" y="116" font-size="11" fill="#64748b">document</text>

  <!-- ─── CHATBOT ─── -->
  <rect x="200" y="134" width="380" height="52" rx="10" fill="#faf5ff" stroke="#9333ea" stroke-width="1.5" filter="url(#sh)"/>
  <text x="390" y="158" text-anchor="middle" font-weight="700" fill="#6b21a8" font-size="14">Summary Chatbot</text>
  <text x="390" y="175" text-anchor="middle" font-size="11" fill="#7e22ce">UI + Conversation Memory</text>
  <line x1="390" y1="186" x2="390" y2="222" stroke="#555" stroke-width="1.4" marker-end="url(#arr)"/>

  <!-- ─── AGENT GRAPH BOX ─── -->
  <rect x="50" y="226" width="680" height="260" rx="14" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="6 3" filter="url(#sh)"/>
  <text x="70" y="250" font-size="12" font-weight="700" fill="#475569">Reflection Agent (LangGraph)</text>

  <!-- START -->
  <circle cx="130" cy="310" r="16" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2"/>
  <text x="130" y="314" text-anchor="middle" font-size="10" font-weight="700" fill="#334155">START</text>
  <line x1="146" y1="310" x2="210" y2="310" stroke="#555" stroke-width="1.3" marker-end="url(#arr)"/>

  <!-- Summarizer node -->
  <rect x="214" y="284" width="200" height="54" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
  <text x="314" y="306" text-anchor="middle" font-weight="700" fill="#1e40af" font-size="13">Summarizer</text>
  <text x="314" y="324" text-anchor="middle" font-size="10" fill="#3b82f6">Generate / Revise summary</text>

  <!-- Arrow: Summarizer → Conditional edge -->
  <line x1="414" y1="311" x2="470" y2="311" stroke="#2563eb" stroke-width="1.3" marker-end="url(#arr-b)"/>

  <!-- Conditional edge diamond -->
  <polygon points="510,290 545,311 510,332 475,311" fill="#fff7ed" stroke="#ea580c" stroke-width="1.3"/>
  <text x="510" y="308" text-anchor="middle" font-size="8" font-weight="700" fill="#c2410c">should</text>
  <text x="510" y="320" text-anchor="middle" font-size="8" font-weight="700" fill="#c2410c">continue?</text>

  <!-- YES: Conditional → Reviewer -->
  <line x1="510" y1="332" x2="510" y2="390" stroke="#ea580c" stroke-width="1.3" marker-end="url(#arr)"/>
  <text x="520" y="366" font-size="10" font-weight="600" fill="#ea580c">yes</text>

  <!-- Reviewer node -->
  <rect x="400" y="394" width="220" height="54" rx="10" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>
  <text x="510" y="416" text-anchor="middle" font-weight="700" fill="#854d0e" font-size="13">Reviewer</text>
  <text x="510" y="434" text-anchor="middle" font-size="10" fill="#a16207">Critique summary · Provide feedback</text>

  <!-- Loop back: Reviewer → Summarizer -->
  <path d="M 400 420 Q 160 420 160 330 Q 160 311 214 311" stroke="#16a34a" stroke-width="1.3" fill="none" marker-end="url(#arr-g)"/>
  <text x="148" y="380" font-size="10" fill="#16a34a" transform="rotate(-90,148,380)">feedback in state</text>

  <!-- NO: Conditional → END -->
  <line x1="545" y1="311" x2="650" y2="311" stroke="#ea580c" stroke-width="1.3" marker-end="url(#arr)"/>
  <text x="590" y="303" font-size="10" font-weight="600" fill="#ea580c">no (done)</text>

  <!-- END -->
  <circle cx="670" cy="311" r="16" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2"/>
  <text x="670" y="315" text-anchor="middle" font-size="10" font-weight="700" fill="#334155">END</text>

  <!-- Agent State bar -->
  <rect x="100" y="464" width="580" height="36" rx="6" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>
  <text x="390" y="486" text-anchor="middle" font-weight="600" fill="#065f46" font-size="12">Agent State — messages: [user input, summaries, reviews, ...]</text>

  <!-- Answer arrow back -->
  <line x1="350" y1="226" x2="350" y2="186" stroke="#555" stroke-width="1.2" stroke-dasharray="5 3" marker-end="url(#arr)"/>
  <text x="310" y="210" font-size="11" fill="#64748b">summary</text>
  <line x1="350" y1="134" x2="350" y2="92" stroke="#555" stroke-width="1.2" stroke-dasharray="5 3" marker-end="url(#arr)"/>

  <!-- ─── LEGEND ─── -->
  <rect x="50" y="560" width="680" height="36" rx="6" fill="#f1f5f9"/>
  <circle cx="80" cy="578" r="6" fill="#dbeafe" stroke="#2563eb"/>
  <text x="92" y="582" font-size="11" fill="#475569">Summarizer</text>
  <polygon points="195,572 207,578 195,584 183,578" fill="#fff7ed" stroke="#ea580c" stroke-width="1"/>
  <text x="213" y="582" font-size="11" fill="#475569">Conditional edge</text>
  <circle cx="330" cy="578" r="6" fill="#fef9c3" stroke="#ca8a04"/>
  <text x="342" y="582" font-size="11" fill="#475569">Reviewer</text>
  <circle cx="420" cy="578" r="6" fill="#ecfdf5" stroke="#059669"/>
  <text x="432" y="582" font-size="11" fill="#475569">Agent State</text>
  <circle cx="520" cy="578" r="6" fill="#faf5ff" stroke="#9333ea"/>
  <text x="532" y="582" font-size="11" fill="#475569">Chatbot</text>
  <line x1="600" y1="578" x2="630" y2="578" stroke="#16a34a" stroke-width="1.3"/>
  <text x="636" y="582" font-size="11" fill="#475569">Loop back</text>
</svg>

---

## Graph Design — Step by Step

The graph implements the **reflection loop** (Generate → Review → Revise → Repeat):

### 1. START → Summarizer

The graph begins at the **Summarizer** node. It reads the user's document (and any previous summaries/feedback) from the agent state. The LLM generates a summary of the input text, prepending the summarizer system prompt to guide concise output.

The Summarizer node writes its output as a new message to the **agent state**.

### 2. Conditional Edge — Should Continue?

A **conditional edge** checks the iteration count stored in the agent state:
- **If fewer than N iterations are done** → route to the **Reviewer** node (continue improving)
- **If N iterations are complete** → route to **END** (the summary is good enough)

The iteration count is derived from the message count: each generate/review cycle adds 2 messages. With the initial user message, after N iterations the state has `1 + 2*N` messages.

### 3. Reviewer Node

The Reviewer node reads the full message history from the agent state — the original document, all previous summaries, and all previous reviews. It uses a reviewer system prompt to critique the summary:
- Does the summary accurately reflect the document?
- What information is missing or could be improved?
- Specific recommendations in under 50 words

The reviewer's feedback is written back to the agent state as a new message.

### 4. Loop Back to Summarizer

Control returns to the Summarizer node. This time, it sees:
- The original document (first user message)
- Its previous summary
- The reviewer's feedback

It uses all of this context to produce a **revised summary** that incorporates the feedback. The cycle continues for up to N iterations.

### 5. END

When the conditional edge determines the maximum iterations are reached, the graph ends. The last message in the agent state is the final refined summary, which is returned to the user.

---

## Data Flow Through Agent State

All data is exchanged through the **agent state**, never through edges. Edges only transfer control.

```
┌──────────────────────────────────────────────────────────────────┐
│                        AGENT STATE                                │
│                                                                    │
│  messages:                                                         │
│    [0] HumanMessage  — original document text                      │
│    [1] AIMessage     — first summary (from summarizer)             │
│    [2] AIMessage     — first review  (from reviewer)               │
│    [3] AIMessage     — revised summary (from summarizer)           │
│    [4] AIMessage     — second review (from reviewer)               │
│    [5] AIMessage     — final summary (from summarizer)   ← output  │
└──────────────────────────────────────────────────────────────────┘

  Summarizer writes summary ──►  Reviewer reads & critiques ──►  Summarizer revises
```

---

## Reflection vs. Other Patterns

| Pattern | How It Works | When to Use |
|---------|-------------|-------------|
| **Tool Use (ReAct)** | LLM decides which external tools to call, observes results, reasons again | Need to interact with external APIs, databases, or calculators |
| **Planning (Supervisor)** | Supervisor routes tasks to specialized sub-agents | Complex multi-domain tasks requiring different expertise |
| **Reflection** | Generator produces output, reviewer critiques it, generator revises | Quality improvement through self-critique — writing, summarization, code review |

---

## Component Summary

| Component | Role | Implementation |
|-----------|------|----------------|
| **Summary Chatbot** | User interface + conversation memory | Accepts documents, maintains history, displays refined summaries |
| **Summarizer node** | Generates/revises summaries | LLM node — calls `model.invoke(messages)` with summarizer prompt |
| **Reviewer node** | Critiques summaries, provides feedback | LLM node — calls `model.invoke(messages)` with reviewer prompt |
| **Conditional edge** | Controls iteration count | `should_continue` — returns `True` if under max iterations |
| **Agent State** | Shared memory for all nodes | Stores original document, summaries, and reviews as messages |
| **MemorySaver** | Conversation persistence per thread | Enables follow-up questions across turns |

---

## Input Document

The example uses `data/ecosprint_specification.txt` — a product specification document for the EcoSprint electric vehicle. It covers:

| Section | Content |
|---------|---------|
| Overview | Revolutionary EV designed for efficiency and performance |
| Design | Aerodynamic exterior, luxurious interior, three color options |
| Performance | 200 HP, 300 Nm, 50 kWh battery, 250-mile range, 0-60 in 7.3s |
| Technology | 10-inch touchscreen, adaptive cruise control, smartphone app |
| Safety | Multiple airbags, reinforced frame, blind-spot monitoring, GPS tracking |

---

## Example Interactions

**Single reflection run (debug mode):**
```
Summarizer output:
  The EcoSprint is a cutting-edge EV designed for eco-friendly drivers...

Reviewer output:
  The summary accurately reflects the document but could improve by
  highlighting acceleration, top speed, and available colors...

Summarizer output (revised):
  The EcoSprint is a cutting-edge EV with a modern design, 200 HP motor,
  250-mile range, and 7.3s acceleration. Available in Midnight Black,
  Ocean Blue, and Pearl White...
```

**Multi-turn conversation:**
```
User: [provides EcoSprint specification document]
Agent: The EcoSprint is an electric vehicle designed for efficiency, with
       200 horsepower and a 250-mile range...

User: Can you rewrite the summary by focusing more on the specifications?
Agent: The EcoSprint offers 200 HP, 300 Nm torque, 50 kWh battery, 250-mile
       range, 0-60 mph in 7.3 seconds, top speed 120 mph...

User: Can you remove details about the touchscreen?
Agent: The EcoSprint delivers 200 HP, 300 Nm torque, 50 kWh battery, 250-mile
       range, 7.3s acceleration. Includes adaptive cruise control and advanced
       safety features...
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
| **Reflection pattern** | Two LLM nodes (summarizer + reviewer) iteratively improve output without external tools |
| **LLM node (summarizer)** | Generates/revises summaries based on document and feedback |
| **LLM node (reviewer)** | Critiques summaries and provides improvement recommendations |
| **Basic edge** | Reviewer → Summarizer (always loop back after review) |
| **Conditional edge** | After Summarizer — checks if max iterations reached |
| **Agent State** | Shared memory that nodes read/write; no data flows through edges |
| **START / END** | Entry and exit points of the graph |
| **MemorySaver** | Conversation memory per `thread_id` for multi-turn follow-ups |

---

## Run

```bash
pip install langchain-openai python-dotenv langgraph
python langgraph_examples/example10_reflection_agent.py
```

Or open [`langgraph_examples/Reflection Agent.ipynb`](../langgraph_examples/Reflection%20Agent.ipynb) and run the cells.
