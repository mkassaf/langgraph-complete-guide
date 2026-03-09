"""
Python Prerequisites — Runnable examples for LangGraph tutorials.
Run: python prerequisites.py

Covers: variables, lists, dicts, functions, type hints, TypedDict, node functions,
dict unpacking, decorators, imports.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Variables and Types
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("1. Variables and Types")
print("=" * 60)

name = "Alice"
count = 42
price = 19.99
is_active = True
value = None

# f-strings for formatting
print(f"Name: {name}, Count: {count}")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Lists (ordered collections)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("2. Lists")
print("=" * 60)

fruits = ["apple", "banana", "cherry"]
print(fruits[0])    # "apple" (0-based index)
print(fruits[-1])   # "cherry" (negative = from end)

fruits.append("date")
fruits = fruits + ["elderberry"]
print(f"Length: {len(fruits)}")

# List comprehension
squares = [x ** 2 for x in range(5)]
print(f"Squares: {squares}")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Dictionaries (key-value pairs)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("3. Dictionaries")
print("=" * 60)

person = {"name": "Alice", "age": 30, "city": "Boston"}
print(person["name"])           # "Alice"
print(person.get("age"))        # 30
print(person.get("email"))      # None (key not present; .get() avoids KeyError)

person["email"] = "alice@example.com"
person["age"] = 31
print(person)

# Return a dict from a function (pattern used in LangGraph nodes)
def process(data):
    return {"result": data * 2}
print(process(21))  # {"result": 42}

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Functions
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("4. Functions")
print("=" * 60)

def greet(name):
    return f"Hello, {name}!"
print(greet("Alice"))

def power(base, exponent=2):
    return base ** exponent
print(f"power(3) = {power(3)}, power(3, 4) = {power(3, 4)}")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Type Hints
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("5. Type Hints")
print("=" * 60)

def add(a: int, b: int) -> int:
    """Add two integers. Returns their sum."""
    return a + b
print(f"add(1, 2) = {add(1, 2)}")

def process_items(items: list[str]) -> dict:
    """Takes a list of strings, returns a dict."""
    return {"count": len(items)}
print(process_items(["apple", "banana", "cherry"]))

# ═══════════════════════════════════════════════════════════════════════════════
# 6. Classes and TypedDict
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("6. Classes and TypedDict")
print("=" * 60)

class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hi, I'm {self.name}"

alice = Person("Alice", 30)
print(alice.greet())

# TypedDict — defines the shape of a dict (used for LangGraph state)
from typing import TypedDict

class State(TypedDict):
    text: str
    count: int

def my_node(state: State) -> dict:
    """Node that appends '!' to text."""
    return {"text": state["text"] + "!"}
print(my_node({"text": "Hello", "count": 1}))

# ═══════════════════════════════════════════════════════════════════════════════
# 7. Node Function + Dict Unpacking (LangGraph pattern)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("7. Node Function + Dict Unpacking")
print("=" * 60)

# Node function: (state) -> dict. LangGraph merges the returned dict into state.
def node_a(state: State) -> dict:
    return {"text": state["text"] + " → A"}

def node_b(state: State) -> dict:
    return {"text": state["text"] + " → B"}

# Dict unpacking: {**d1, **d2} merges d2 into d1 (d2 overwrites shared keys)
a = {"x": 1, "y": 2}
b = {"y": 99, "z": 3}
merged = {**a, **b}  # {"x": 1, "y": 99, "z": 3}
print(f"Merge example: {{**a, **b}} = {merged}")

# Simulate graph run: A → B (LangGraph does this internally)
state = {"text": "START", "count": 0}
state = {**state, **node_a(state)}  # Merge node_a's return into state
state = {**state, **node_b(state)}  # Merge node_b's return into state
print(f"After A→B: {state}")

# ═══════════════════════════════════════════════════════════════════════════════
# 8. Decorators
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("8. Decorators")
print("=" * 60)

def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("  Before")
        result = func(*args, **kwargs)
        print("  After")
        return result
    return wrapper

@my_decorator
def say_hello():
    print("  Hello!")

say_hello()

# ═══════════════════════════════════════════════════════════════════════════════
# 9. Imports and Environment
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("9. Imports and Environment")
print("=" * 60)

import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env into os.environ
model = os.environ.get("MODEL", "not set")
print(f"MODEL from .env: {model}")

print("\nDone.")
