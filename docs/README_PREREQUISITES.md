# Python Prerequisites for LangGraph Examples

> **Who this is for:** Anyone new to Python or needing a quick refresher before diving into the [LangGraph examples](README.md).
> **Goal:** Understand the Python concepts used in this repository's examples.

**Reading order:** [README_PREREQUISITES.md](README_PREREQUISITES.md) (you are here) → [README_LANGCHAIN.md](README_LANGCHAIN.md) → [README.md](README.md)

---

## Table of Contents

1. [What You Need](#1-what-you-need)
2. [Variables and Types](#2-variables-and-types)
3. [Lists and Dictionaries](#3-lists-and-dictionaries)
4. [Functions](#4-functions)
5. [Type Hints](#5-type-hints)
6. [Classes and TypedDict](#6-classes-and-typeddict)
7. [Decorators](#7-decorators)
8. [Imports](#8-imports)
9. [Quick Reference](#9-quick-reference)

---

## 1. What You Need

- **Python 3.10+** (3.11 or 3.12 recommended)
- **Basic familiarity** with running commands in a terminal
- **A text editor or IDE** (VS Code, PyCharm, or Cursor)

Check your Python version:
```bash
python --version
# or
python3 --version
```

---

## 2. Variables and Types

Python is dynamically typed — you don't declare types, but understanding them helps.

```python
# Strings (text)
name = "Alice"
greeting = 'Hello, world!'
multiline = """This spans
multiple lines."""

# Numbers
count = 42          # int (integer)
price = 19.99        # float (decimal)
result = 2 ** 10     # 1024 (exponentiation)

# Booleans
is_active = True
is_done = False

# None (absence of value)
value = None
```

**String formatting (f-strings):**
```python
x, y = 3, 5
print(f"The sum of {x} and {y} is {x + y}")  # The sum of 3 and 5 is 8
```

---

## 3. Lists and Dictionaries

### Lists (ordered collections)

```python
# Create a list
fruits = ["apple", "banana", "cherry"]

# Access by index (0-based)
first = fruits[0]   # "apple"
last = fruits[-1]   # "cherry" (negative index = from end)

# Add items
fruits.append("date")
fruits = fruits + ["elderberry"]  # concatenate lists

# Length
len(fruits)  # 5

# List comprehension (create list from another)
squares = [x ** 2 for x in range(5)]  # [0, 1, 4, 9, 16]
```

### Dictionaries (key-value pairs)

```python
# Create a dict
person = {"name": "Alice", "age": 30, "city": "Boston"}

# Access by key
print(person["name"])   # Alice
print(person.get("age"))  # 30 (safer; returns None if key missing)

# Add or update
person["email"] = "alice@example.com"
person["age"] = 31

# Keys and values
person.keys()    # dict_keys(['name', 'age', 'city', 'email'])
person.values()  # dict_values([...])

# Return a dict from a function (used in LangGraph nodes)
def process(data):
    return {"result": data * 2}  # Returns a dict
```

**Why this matters for LangGraph:** Graph nodes receive `state` (a dict) and return a dict of updates. Example: `return {"text": new_text}`.

---

## 4. Functions

```python
# Basic function
def greet(name):
    return f"Hello, {name}!"

greet("Alice")  # "Hello, Alice!"

# With default argument
def power(base, exponent=2):
    return base ** exponent

power(3)      # 9 (uses default exponent=2)
power(3, 4)  # 81

# With type hints (see next section)
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b
```

**Docstrings** (triple-quoted string right after `def`):
```python
def my_function(x):
    """
    Brief description of what the function does.
    The LLM reads docstrings when deciding which tool to call!
    """
    return x * 2
```

---

## 5. Type Hints

Type hints tell readers (and tools) what types a function expects. They don't change runtime behavior.

```python
def add(a: int, b: int) -> int:
    """Add two integers. Returns their sum."""
    return a + b

def process(items: list[str]) -> dict:
    """Takes a list of strings, returns a dict."""
    return {"count": len(items)}
```

**Common types:**
- `str`, `int`, `float`, `bool`
- `list[T]` — list of type T (e.g. `list[str]`)
- `dict` or `dict[K, V]`
- `Optional[T]` — value is T or None
- `Literal["a", "b"]` — must be one of these exact values

```python
from typing import Literal

def route(choice: Literal["math", "research", "finish"]) -> str:
    return choice  # Must be one of the three
```

---

## 6. Classes and TypedDict

### Simple class

```python
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hi, I'm {self.name}"
```

### TypedDict (used for LangGraph state)

`TypedDict` defines the "shape" of a dictionary — which keys it has and their types. LangGraph uses this for state.

```python
from typing import TypedDict

class State(TypedDict):
    text: str
    count: int

# Now we know state has "text" (str) and "count" (int)
def my_node(state: State) -> dict:
    current = state["text"]   # Type checker knows this is str
    return {"text": current + "!"}  # Return partial update
```

**Why TypedDict?** It documents the state structure and enables IDE autocomplete. The graph merges returned dicts into the state.

---

## 7. Decorators

A decorator wraps a function to add behavior. The `@` syntax applies it.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before calling function")
        result = func(*args, **kwargs)
        print("After calling function")
        return result
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# Before calling function
# Hello!
# After calling function
```

**In LangGraph:** The `@tool` decorator turns a function into a LangChain tool the LLM can call:

```python
from langchain_core.tools import tool

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers. Use for any addition."""
    return a + b
# add_numbers is now a tool with name, description, and parameter schema
```

---

## 8. Imports

```python
# Import a module
import os
os.environ["KEY"]  # Access via module name

# Import specific items
from typing import TypedDict, Literal

# Import with alias
from langchain_openai import ChatOpenAI as OpenAI

# Import from a package
from langgraph.graph import StateGraph, START, END
```

**Common imports in our examples:**
```python
from typing import TypedDict, Literal, Annotated
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from dotenv import load_dotenv  # Loads .env file into environment variables
```

---

## 9. Quick Reference

| Concept | Example |
|---------|---------|
| Variable | `x = 42` |
| List | `items = [1, 2, 3]` |
| Dict | `d = {"key": "value"}` |
| Function | `def f(x): return x + 1` |
| Type hint | `def f(x: int) -> str:` |
| TypedDict | `class S(TypedDict): x: str` |
| Decorator | `@tool` above a function |
| f-string | `f"Result: {x}"` |
| Docstring | `"""Description"""` after `def` |

---

## Next Steps

1. **Run the examples** — Start with `langgraph_examples/example1_hello_world.py`
2. **LangChain basics** — Read [README_LANGCHAIN.md](README_LANGCHAIN.md) for models, prompts, chains, tools
3. **LangGraph tutorial** — Follow [README.md](README.md) from Example 1 onward

---

*This guide covers the Python used in our LangGraph examples. For a full Python tutorial, see [python.org](https://docs.python.org/3/tutorial/).*
