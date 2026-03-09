# file: langgraph_examples/example9_orders_agent.py
"""
Orders Agent & Chatbot — Query and Update Laptop Orders
────────────────────────────────────────────────────────
A custom agentic chatbot that can answer questions about laptop orders
AND perform actions (update orders). It uses a manually built LangGraph
StateGraph rather than the prebuilt `create_react_agent`.

Key concepts demonstrated:
  - Custom StateGraph: Manually wired graph with LLM node, tool node,
    and conditional edge — the same ReAct loop but built by hand.
  - OrdersAgent class: Encapsulates the graph, tools, and LLM in a
    reusable class with a debug flag.
  - Two function tools:
      get_order_details — READ: Returns order details for an order ID
      update_quantity   — WRITE: Updates laptop quantity in an order
  - MemorySaver: Conversation memory per thread_id, so "Can you add
    one more?" refers to the order the user was just asking about.
  - Agent State: All data flows through the state (messages list),
    never through edges. Edges only transfer control.

Graph design:
  START → orders_llm → [is_tool_call?] → orders_tools (if yes) → orders_llm
                                        → END (if no — final answer ready)

See also: docs/README_ORDERS_AGENT.md for architecture diagram and design doc.
"""

import json
import uuid
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
import operator

load_dotenv()

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ORDERS_CSV = DATA_DIR / "laptop_orders.csv"


# ─── 1. Setup LLM ────────────────────────────────────────────────────────────
# ChatOpenAI: Uses OPENAI_API_KEY from .env. temperature=0 for deterministic output.
# To use Azure OpenAI instead, replace with AzureChatOpenAI and set the corresponding
# environment variables (AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT).
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─── 2. Load Orders Data ─────────────────────────────────────────────────────
# The orders "database" is a Pandas DataFrame loaded from CSV.
# In a real application, this would be an RDBMS (PostgreSQL, MySQL, etc.).
# Columns: Order ID, Product Ordered, Quantity Ordered, Delivery Date
product_orders_df = pd.read_csv(ORDERS_CSV)


# ─── 3. Define Tools ─────────────────────────────────────────────────────────
# Two function tools: one for READING order details, one for WRITING (updating quantity).
# The @tool decorator turns each function into a LangChain tool. The LLM reads the
# docstring to decide WHEN to call the tool and what arguments to provide.

@tool
def get_order_details(order_id: str) -> str:
    """
    Return details about a laptop order given an order ID.
    Performs an exact match on the Order ID column.
    If found, returns: product ordered, quantity, and delivery date.
    If NOT found, returns -1.
    """
    match_order_df = product_orders_df[
        product_orders_df["Order ID"] == order_id
    ]

    if len(match_order_df) == 0:
        return -1
    else:
        return match_order_df.iloc[0].to_dict()

print(get_order_details("ORD-7311"))

@tool
def update_quantity(order_id: str, new_quantity: int) -> bool:
    """
    Update the quantity of laptops ordered for a given order ID.
    If the order exists, updates the Quantity Ordered field and returns True.
    If there is NO matching order, returns False.
    """
    # We need to declare global so we can modify the module-level DataFrame
    global product_orders_df

    match_order_df = product_orders_df[
        product_orders_df["Order ID"] == order_id
    ]

    if len(match_order_df) == 0:
        return False
    else:
        product_orders_df.loc[
            product_orders_df["Order ID"] == order_id,
            "Quantity Ordered"
        ] = new_quantity
        return True


# ─── 4. Agent State ──────────────────────────────────────────────────────────
# The agent state holds the list of messages exchanged during the conversation.
# `operator.add` means new messages are APPENDED (not replaced) when a node returns
# {"messages": [new_msg]}. This is essential for conversation history to accumulate.

class OrdersAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


# ─── 5. OrdersAgent Class ────────────────────────────────────────────────────
# Encapsulates the entire agent: graph, LLM, tools, and memory.
# This is a manual build of the ReAct pattern (compare with create_react_agent
# which does the same thing in one line, but gives you less control).

class OrdersAgent:

    def __init__(self, model, tools, system_prompt, debug=False):
        """
        Build the agent graph manually.

        Parameters:
          model        — A LangChain chat model (e.g., ChatOpenAI)
          tools        — List of @tool-decorated functions
          system_prompt — String prepended to messages for the LLM's persona
          debug        — If True, prints intermediate LLM and tool outputs
        """
        self.system_prompt = system_prompt
        self.debug = debug

        # --- Build the graph ---
        # StateGraph(OrdersAgentState): Creates a graph whose shared state is
        # the OrdersAgentState TypedDict (just a messages list).
        agent_graph = StateGraph(OrdersAgentState)

        # Add two nodes:
        #   orders_llm   — LLM node: sends messages to the model, gets actions/answers
        #   orders_tools — Tool node: executes whichever tool the LLM requested
        agent_graph.add_node("orders_llm", self.call_llm)
        agent_graph.add_node("orders_tools", self.call_tools)

        # Conditional edge from orders_llm:
        #   self.is_tool_call inspects the last message. If it contains tool_calls
        #   (the LLM wants to call a tool), route to orders_tools. Otherwise, the
        #   final answer is ready — route to END.
        agent_graph.add_conditional_edges(
            "orders_llm",
            self.is_tool_call,
            {True: "orders_tools", False: END}
        )

        # Basic edge: after tools execute, always loop back to orders_llm
        # so it can review the tool results and decide next steps.
        agent_graph.add_edge("orders_tools", "orders_llm")

        # Set the entry point (equivalent to add_edge(START, "orders_llm"))
        agent_graph.set_entry_point("orders_llm")

        # MemorySaver: Stores conversation state per thread_id.
        # Different thread_ids = different conversations (multi-user).
        self.memory = MemorySaver()

        # Compile: Turns the graph definition into a runnable app.
        self.agent_graph = agent_graph.compile(checkpointer=self.memory)

        # Store tools in a dict keyed by name for easy lookup in call_tools.
        self.tools = {t.name: t for t in tools}
        if self.debug:
            print("\nTools loaded:", list(self.tools.keys()))

        # bind_tools: Tells the LLM what tools are available. After binding,
        # the model can return AIMessage(tool_calls=[...]) instead of plain text.
        self.model = model.bind_tools(tools)

    def call_llm(self, state: OrdersAgentState):
        """
        LLM node: Read messages from state, prepend system prompt, invoke LLM.

        The LLM either:
          a) Returns an AIMessage with tool_calls → the conditional edge routes to tools
          b) Returns an AIMessage with content (final answer) → routes to END
        """
        messages = state["messages"]

        if self.system_prompt:
            messages = [SystemMessage(content=self.system_prompt)] + messages

        result = self.model.invoke(messages)
        if self.debug:
            print(f"\nLLM returned: {result}")
        return {"messages": [result]}

    def is_tool_call(self, state: OrdersAgentState):
        """
        Conditional edge function: Check if the LLM's last message requests a tool.

        Returns True if tool_calls are present (route to orders_tools),
        False otherwise (route to END — final answer is ready).
        """
        last_message = state["messages"][-1]
        return len(last_message.tool_calls) > 0

    def call_tools(self, state: OrdersAgentState):
        """
        Tool node: Execute the tools requested by the LLM.

        Steps:
          1. Read tool_calls from the last AIMessage
          2. For each tool call, look up the tool by name and invoke it
          3. Wrap results in ToolMessage (with matching tool_call_id)
          4. Return messages to be appended to state

        The LLM may request multiple tool calls in one turn (e.g., get details
        then update quantity). Each is executed and its result is returned.
        """
        tool_calls = state["messages"][-1].tool_calls
        results = []

        for tc in tool_calls:
            if tc["name"] not in self.tools:
                print(f"Unknown tool: {tc['name']}")
                result = "Invalid tool found. Please retry."
            else:
                result = self.tools[tc["name"]].invoke(tc["args"])

            results.append(
                ToolMessage(
                    tool_call_id=tc["id"],
                    name=tc["name"],
                    content=str(result),
                )
            )

        if self.debug:
            print(f"\nTools returned: {results}")
        return {"messages": results}


# ─── 6. Create the Orders Agent ──────────────────────────────────────────────
# System prompt: Defines the chatbot's persona and rules.
# - "Do NOT reveal information about other orders" — privacy guardrail
# - "Handle small talk" — for greetings like "Hello" or "Bye"

SYSTEM_PROMPT = """
You are a professional chatbot that manages orders for laptops sold by our company.
The tools allow for retrieving order details as well as updating order quantity.
Do NOT reveal information about other orders than the one requested.
You will handle small talk and greetings by producing professional responses.
"""

orders_agent = OrdersAgent(
    model,
    [get_order_details, update_quantity],
    SYSTEM_PROMPT,
    debug=False,
)


# ─── 7. Run Examples ─────────────────────────────────────────────────────────

def run_conversation():
    """
    Simulates a multi-turn conversation with the orders chatbot.

    The conversation demonstrates:
      - Small talk ("How are you doing?")
      - Querying an order (get_order_details for ORD-7311)
      - Updating an order ("add one more" → update_quantity)
      - Verifying the update ("show me the details again")
      - Handling a missing order (ORD-9999)
      - Farewell ("Bye")

    All messages share the same thread_id, so the agent remembers context.
    "Can you add one more of that laptop" works because it remembers ORD-7311.
    """
    user_inputs = [
        "How are you doing?",
        "Please show me the details of the order ORD-7311",
        "Can you add one more of that laptop to the order?",
        "Can you show me the details again?",
        "What about order ORD-9999?",
        "Bye",
    ]

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    for user_input in user_inputs:
        print(f"{'─' * 40}\nUSER  : {user_input}")
        user_message = {"messages": [HumanMessage(user_input)]}
        ai_response = orders_agent.agent_graph.invoke(user_message, config=config)
        print(f"AGENT : {ai_response['messages'][-1].content}\n")


def run_multi_user():
    """
    Two users with different thread_ids — each has separate memory.

    USER 1 asks about ORD-8276, USER 2 asks about ORD-6948.
    "What about that order?" refers to each user's own order.
    """
    print("=" * 60)
    print("Multi-user demo (separate memory per thread_id)")
    print("=" * 60)

    def ask(user_label: str, config: dict, prompt: str):
        result = orders_agent.agent_graph.invoke(
            {"messages": [HumanMessage(content=prompt)]},
            config=config,
        )
        print(f"\n{user_label}: {result['messages'][-1].content}")

    config_1 = {"configurable": {"thread_id": str(uuid.uuid4())}}
    config_2 = {"configurable": {"thread_id": str(uuid.uuid4())}}

    ask("USER 1", config_1, "Show me order ORD-8276")
    ask("USER 2", config_2, "Show me order ORD-6948")
    ask("USER 1", config_1, "Update the quantity to 5")
    ask("USER 2", config_2, "Update the quantity to 1")
    ask("USER 1", config_1, "Show me the details again")
    ask("USER 2", config_2, "Show me the details again")


if __name__ == "__main__":
    print("=" * 60)
    print("Orders Agent — Multi-turn Conversation")
    print("=" * 60)
    run_conversation()

    print("\n")
    run_multi_user()
