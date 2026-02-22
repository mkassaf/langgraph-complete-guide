# LangChain Complete Guide for Researchers
## From Zero to AI Agents with Building Blocks

> **Who this is for:** PhD students and researchers with Python knowledge but zero LangChain experience.
> **Goal:** Master LangChain's building blocks (models, prompts, chains, tools) step by step — from simple LLM calls to agents that use tools.

All examples live in the [`langchain_examples/`](langchain_examples/) folder.

---

## Table of Contents

1. [What is LangChain? (Conceptual Overview)](#1-what-is-langchain)
2. [Environment Setup](#2-environment-setup)
3. [Core Concepts You Must Understand First](#3-core-concepts)
4. [Example 1 — Simple LLM Call (No Prompts, No Chains)](#4-example-1-simple-llm-call)
5. [Example 2 — Prompt Templates](#5-example-2-prompt-templates)
6. [Example 3 — LCEL Chains (Pipe Your Steps)](#6-example-3-lcel-chains)
7. [Example 4 — Output Parsers & Structured Output](#7-example-4-output-parsers)
8. [Example 5 — Tools (Functions the LLM Can Call)](#8-example-5-tools)
9. [Example 6 — Simple Agent with Tools](#9-example-6-agent-with-tools)
10. [Quick Reference Cheat Sheet](#10-cheat-sheet)

---

## 1. What is LangChain?

Imagine you want to build an AI research assistant. You need to:

1. Call an LLM with your question.
2. Maybe format the question with a template.
3. Parse the response into a structured format.
4. Sometimes let the LLM call functions (search, calculate, etc.).

Each of these is a **building block**. LangChain provides them ready to use.

**LangChain** is a Python library that gives you:

- **Models**: A standard interface to call OpenAI, Anthropic, Ollama, and many others.
- **Prompts**: Templates to structure your inputs.
- **Chains**: Connect steps together (prompt → model → parser).
- **Tools**: Functions the LLM can decide to call (calculator, web search, etc.).

**LangChain vs LangGraph:**
- **LangChain** = The LEGO pieces (models, prompts, tools).
- **LangGraph** = The orchestration layer (graphs, state, loops). See [README.md](README.md) for LangGraph.
- Together they let you build complex multi-agent systems.

---

## 2. Environment Setup

### Step 1: Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows
```

### Step 2: Install Required Packages

```bash
pip install -U langchain langchain-openai langchain-core python-dotenv
```

### Step 3: Get an API Key

Set up your `.env` file with:

```
OPENAI_API_KEY=sk-your-key-here
```

See the main [README.md](README.md) §2 for full setup details (Anthropic, Ollama options, etc.).

---

## 3. Core Concepts

### 3.1 Models — Talking to the LLM

LangChain wraps each provider (OpenAI, Anthropic, etc.) in a common interface. You call `invoke()` with messages and get a response.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
response = llm.invoke("What is 2+2?")
print(response.content)  # "4"
```

### 3.2 Prompts — Templates for Input

Instead of hardcoding strings, use templates with placeholders:

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}."),
    ("human", "{question}")
])
```

### 3.3 Chains — Connecting Steps

A **chain** links prompt → model → (optional) parser. You build it with the pipe operator `|` (LCEL).

```python
chain = prompt | llm
result = chain.invoke({"role": "tutor", "question": "Explain recursion"})
```

### 3.4 Tools — Functions the LLM Can Call

A **tool** is a Python function decorated with `@tool`. The LLM reads the docstring and arguments to decide when to call it.

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

---

## 4. Example 1 — Simple LLM Call (No Prompts, No Chains)

The simplest use: create an LLM, send a message, get a reply.

```python
# file: langchain_examples/langchain_example1_simple_llm.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Option A: Plain string (treated as user message)
response = llm.invoke("What is the capital of France?")
print(response.content)

# Option B: Explicit messages (for system + user)
messages = [
    SystemMessage(content="You are a concise geography tutor."),
    HumanMessage(content="What is the capital of France?")
]
response = llm.invoke(messages)
print(response.content)
```

**Run it:**
```bash
python langchain_examples/langchain_example1_simple_llm.py
```

**Key takeaway:** `ChatOpenAI.invoke()` accepts a string or a list of messages. The response has a `.content` attribute with the text.

---

## 5. Example 2 — Prompt Templates

Use templates to inject variables and keep prompts maintainable.

```python
# file: langchain_examples/langchain_example2_prompts.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Create a template with placeholders
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Answer briefly and clearly."),
    ("human", "{question}")
])

# Fill in the variables
messages = prompt.format_messages(role="math tutor", question="What is 15% of 80?")
response = llm.invoke(messages)

print(response.content)
```

**Key takeaway:** `ChatPromptTemplate.from_messages()` lets you define reusable prompts with `{variable}` placeholders.

---

## 6. Example 3 — LCEL Chains (Pipe Your Steps)

**LCEL** (LangChain Expression Language) uses the `|` operator to chain components. Output of one step flows as input to the next.

```python
# file: langchain_examples/langchain_example3_chain.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Be concise."),
    ("human", "{question}")
])

# Chain: prompt | llm | parser
# The parser converts the LLM's AIMessage to a plain string
parser = StrOutputParser()
chain = prompt | llm | parser

# Invoke with a dict of template variables
result = chain.invoke({"role": "research assistant", "question": "What is a transformer in NLP?"})
print(result)  # Plain string, not an AIMessage
```

**Key takeaway:** `prompt | llm | parser` creates a runnable chain. `invoke()` returns the output of the last step.

---

## 7. Example 4 — Output Parsers & Structured Output

Sometimes you want structured data (e.g., JSON, a Pydantic model) instead of raw text.

```python
# file: langchain_examples/langchain_example4_structured_output.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

load_dotenv()

class ResearchSummary(BaseModel):
    """Structured research summary."""
    key_points: list[str] = Field(description="List of 3 key points")
    conclusion: str = Field(description="One-sentence conclusion")
    confidence: str = Field(description="low, medium, or high")

parser = PydanticOutputParser(pydantic_object=ResearchSummary)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You summarize research topics. Output valid JSON matching this schema:
{format_instructions}"""),
    ("human", "Summarize: {topic}")
])

chain = prompt | llm | parser
result = chain.invoke({
    "topic": "Large Language Model hallucinations",
    "format_instructions": parser.get_format_instructions()
})

print(result.key_points)
print(result.conclusion)
print(result.confidence)
```

**Key takeaway:** `PydanticOutputParser` forces the LLM output into a Pydantic model. Use `parser.get_format_instructions()` in your prompt so the LLM knows the schema.

---

## 8. Example 5 — Tools (Functions the LLM Can Call)

Tools are functions the LLM can invoke when it needs to (e.g., search, compute). The LLM uses the function name and docstring to decide when to call them.

```python
# file: langchain_examples/langchain_example5_tools.py

from langchain_core.tools import tool

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers. Use for any addition."""
    return a + b

@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers. Use for any multiplication."""
    return a * b

# Tools are callable and have metadata
print(add_numbers.name)       # "add_numbers"
print(add_numbers.description)  # From docstring
print(add_numbers.invoke({"a": 3, "b": 5}))  # 8.0
```

**Key takeaway:** The `@tool` decorator turns a function into a LangChain tool. The docstring is critical — the LLM reads it to decide when to use the tool.

---

## 9. Example 6 — Agent with Tools

An agent is an LLM that can decide to call tools and use their results. This uses LangGraph under the hood; here we show the LangChain-style tool binding.

```python
# file: langchain_examples/langchain_example6_agent.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city. Use when asked about weather."""
    # Mock response — in production, call a real API
    return f"The weather in {city} is sunny, 72°F."

@tool
def add(a: int, b: int) -> int:
    """Add two integers. Use for arithmetic."""
    return a + b

tools = [get_weather, add]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Bind tools to the LLM — now it can choose to call them
llm_with_tools = llm.bind_tools(tools)

# Single invocation — LLM may or may not use tools
response = llm_with_tools.invoke([
    HumanMessage(content="What is 17 + 23? Use a tool if helpful.")
])

print(response.content)
if response.tool_calls:
    for tc in response.tool_calls:
        print(f"Tool: {tc['name']}, args: {tc['args']}")
```

**Note:** A full agent loop (LLM → tool call → run tool → back to LLM) is typically built with LangGraph. See [README.md](README.md) Example 3 for the complete pattern.

**Key takeaway:** `llm.bind_tools(tools)` tells the LLM what tools exist. The response may contain `tool_calls` that your code must execute and feed back.

---

## 10. Quick Reference Cheat Sheet

### Installation
```bash
pip install -U langchain langchain-openai langchain-core python-dotenv
```

### Simple LLM Call
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("Hello")
print(response.content)
```

### Prompt Template + Chain
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([("human", "{input}")])
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"input": "Explain recursion"})
```

### Tools
```python
from langchain_core.tools import tool

@tool
def my_tool(arg: str) -> str:
    """Description the LLM uses to decide when to call this."""
    return f"Result: {arg}"

llm_with_tools = llm.bind_tools([my_tool])
```

### Key Concepts

| Concept | What It Is | Example |
|--------|------------|---------|
| `ChatOpenAI` | LLM wrapper for OpenAI | `llm.invoke(messages)` |
| `ChatPromptTemplate` | Reusable prompt with variables | `prompt.format_messages(**kwargs)` |
| `StrOutputParser` | Converts AIMessage to string | `chain = prompt \| llm \| parser` |
| `PydanticOutputParser` | Parses into Pydantic model | `parser.parse(response)` |
| `@tool` | Decorator for LLM-callable functions | `@tool def f(x): ...` |
| `bind_tools()` | Gives LLM access to tools | `llm.bind_tools([tool1, tool2])` |

---

## Official References

- **[LangGraph Install](https://docs.langchain.com/oss/python/langgraph/install)** — Install LangGraph and LangChain
- **[LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview)** — Introduction and architecture
- **[LangChain Quickstart](https://docs.langchain.com/oss/python/langchain/quickstart)** — Build your first agent with the official quickstart

---

*This guide complements the [LangGraph tutorial](README.md). Use LangChain for building blocks; use LangGraph for orchestration and complex workflows.*
