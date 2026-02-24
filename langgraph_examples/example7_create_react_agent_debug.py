# file: langgraph_examples/example7_create_react_agent_debug.py
"""
create_react_agent with debug=True
─────────────────────────────────
This example uses LangGraph's prebuilt create_react_agent instead of building the
graph manually (StateGraph + ToolNode + tools_condition). create_react_agent is
a one-liner that gives you a full ReAct agent.

The debug=True parameter enables verbose step-by-step output so you can see:
  - [N:checkpoint] — State at the end of each step (full messages, metadata)
  - [N:tasks]     — Which node runs next and what input it receives
  - [N:writes]    — What the node wrote to state (channel + value)

This is useful when:
  - The agent behaves unexpectedly and you want to trace the flow
  - You need to inspect token usage, tool call args, or intermediate state
  - You're learning how the ReAct loop works internally

Compare with example6_react_math_agent.py, which builds the same agent manually
and uses message.pretty_repr() for a cleaner message-only view.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

load_dotenv()

# ─── Tools ─────────────────────────────────────────────────────────────────────
@tool
def find_sum(x: int, y: int) -> int:
    """Add two numbers. Use for any addition."""
    return x + y


@tool
def find_product(x: int, y: int) -> int:
    """Multiply two numbers. Use for any multiplication."""
    return x * y


# ─── Create ReAct Agent ───────────────────────────────────────────────────────
tools = [find_sum, find_product]
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# state_modifier: SystemMessage or str — prepended to messages before each LLM call.
# Same role as the system_prompt in example6.
system_prompt = SystemMessage(content="""You are a Math genius. Solve problems using
ONLY the tools available. Do NOT compute in your head — always call the tool.""")

# debug=False (default): Silent execution, only the final result.
# debug=True: Prints [checkpoint], [tasks], [writes] for every step.
agent = create_react_agent(
    model,
    tools=tools,
    state_modifier=system_prompt,
    debug=True,  # <-- Enables step-by-step debug output
)

# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("Running with debug=True — watch the step-by-step output below")
    print("=" * 60)

    inputs = {"messages": [("user", "what is the sum of 2 and 3?")]}
    result = agent.invoke(inputs)

    print("\n" + "=" * 60)
    print("FINAL ANSWER:", result["messages"][-1].content)
    print("=" * 60)
