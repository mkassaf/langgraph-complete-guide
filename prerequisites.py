# Create a list
fruits = ["apple", "banana", "cherry"]

# Access by index (0-based)
first = fruits[0]   # "apple"
last = fruits[-1]   # "cherry" (negative index = from end)

print(first)
print(last)

print(fruits)
# Add items
fruits.append("date")
print(fruits)
fruits = fruits + ["elderberry"]  # concatenate lists
print(fruits)
# Length
len(fruits)  # 5

# List comprehension (create list from another)
squares = [x ** 2 for x in range(5)]  # [0, 1, 4, 9, 16]


print(squares)

### Dictionaries (key-value pairs)

print("=================================Dictionaries (key-value pairs) =================================")
# Create a dict
person = {"name": "Alice", "age": 30, "city": "Boston"}
print(person)
# Access by key
print(person["name"])   # Alice
print(person.get("age"))  # 30 (safer; returns None if key missing)
print(person.get("email"))  # alice@example.com

# Add or update
person["email"] = "alice@example.com"
person["age"] = 31
print(person)
# Keys and values
person.keys()    # dict_keys(['name', 'age', 'city', 'email'])
person.values()  # dict_values([...])
print(person.keys())
print(person.values())
# Return a dict from a function (used in LangGraph nodes)
def process(data):
    return {"result": data * 2}  # Returns a dict

######### Functions #########

print("=================================Functions =================================")

# Basic function
def greet(name):
    return f"Hello, {name}!"

greet("Alice")  # "Hello, Alice!"
print(greet("Alice"))  # "Hello, Alice!"

# With default argument
def power(base, exponent=2):
    return base ** exponent

print(power(3))  # 9 (uses default exponent=2)
print(power(3, 4))  # 81

# With type hints (see next section)
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

print(add(1.5, 2.5))  # 4.0

print("=================================Type Hints =================================")

# Type hints tell readers (and tools) what types a function expects. They don't change runtime behavior.
def add(a: int, b: int) -> int:
    """Add two integers. Returns their sum."""
    return a + b

print(add(1, 2))  # 3
print(add.__doc__)

def process(items: list[str]) -> dict:
    """Takes a list of strings, returns a dict."""
    return {"count": len(items)}

print(process(["apple", "banana", "cherry"]))  # {"count": 3}

print("================================= Classes and TypedDict =================================")

# Simple class
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hi, I'm {self.name}"


object = Person("Alice", 30)

print(object.name)
print(object.age)
print(object.greet())  # "Hi, I'm Alice"

## TypedDict (used for LangGraph state)

from typing import TypedDict

class State(TypedDict):
    text: str
    count: int

# Now we know state has "text" (str) and "count" (int)
def my_node(state: State) -> dict:
    current = state["text"]   # Type checker knows this is str
    return {"text": current + "!"}  # Return partial update

print(my_node({"text": "Hello", "count": 1}))  # {"text": "Hello!"}
print(my_node({"text": "Hello 2", "count": 2}))

print("=================================Decorators =================================")
# Decorators wrap a function to add behavior. The @ syntax applies it.
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

print("=================================Imports =================================")
# Imports are used to bring in modules (files) into the current file.
import os
import dotenv # Loads .env file into environment variables
dotenv.load_dotenv()  # Loads .env file into environment variables

os.environ["MODEL"]  # Access via module name

print(os.environ["MODEL"])