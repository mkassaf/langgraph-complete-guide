# file: langgraph_examples/example1_hello_world.py

# ─── Imports ─────────────────────────────────────────────────────────────────
from typing import TypedDict          # For defining our state structure
from langgraph.graph import StateGraph, START, END  # Core LangGraph components

# ─── Step 1: Define the State ─────────────────────────────────────────────────
# The state is a typed dictionary — it's like a contract that says 
# "our shared data will always have these fields with these types"

class State(TypedDict):
    text: str   # A simple string that nodes will modify

# ─── Step 2: Define Nodes (Functions) ─────────────────────────────────────────
# Each node is a function that:
#   - Takes the current state as input
#   - Returns a dict with the fields it wants to update

def node_a(state: State) -> dict:
    """Node A appends 'A' to the text."""
    current_text = state["text"]        # Read from state
    new_text = current_text + " → A"   # Do work
    print(f"Node A running. Text is now: '{new_text}'")
    return {"text": new_text}           # Return only what changed

def node_b(state: State) -> dict:
    """Node B appends 'B' to the text."""
    current_text = state["text"]
    new_text = current_text + " → B"
    print(f"Node B running. Text is now: '{new_text}'")
    return {"text": new_text}

def node_c(state: State) -> dict:
    """Node C appends 'C' to the text."""
    current_text = state["text"]
    new_text = current_text + " → C"
    print(f"Node C running. Text is now: '{new_text}'")
    return {"text": new_text}

# ─── Step 3: Build the Graph ──────────────────────────────────────────────────
# Create a StateGraph and tell it what our state looks like
graph = StateGraph(State)

# Add nodes: give each function a string name
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)

# Add edges: define the flow
# START is a special built-in constant meaning "the very beginning"
# END is a special built-in constant meaning "we are done"
graph.add_edge(START, "node_a")   # When graph starts, go to node_a
graph.add_edge("node_a", "node_b")  # After node_a, go to node_b
graph.add_edge("node_b", "node_c")  # After node_b, go to node_c
graph.add_edge("node_c", END)       # After node_c, we are done

# ─── Step 4: Compile the Graph ────────────────────────────────────────────────
# This "compiles" the graph definition into a runnable app
app = graph.compile()

# ─── Step 5: Run It ───────────────────────────────────────────────────────────
# invoke() runs the graph from START to END
# We provide the initial state as a dictionary
initial_state = {"text": "START"}
result = app.invoke(initial_state)

print("\n─── Final Result ───")
print(result)  # {'text': 'START → A → B → C'}