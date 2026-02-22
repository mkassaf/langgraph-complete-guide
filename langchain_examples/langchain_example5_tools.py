# file: langchain_examples/langchain_example5_tools.py
# Example 5 — Tools (Functions the LLM Can Call)

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
print("Tool name:", add_numbers.name)
print("Tool description:", add_numbers.description)
print("add_numbers(3, 5) =", add_numbers.invoke({"a": 3, "b": 5}))
print("multiply_numbers(4, 7) =", multiply_numbers.invoke({"a": 4, "b": 7}))
