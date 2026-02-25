# file: langgraph_examples/example11_multi_agent_router.py
"""
Multi-Agent Router — Routing Pattern with Specialized Agents
─────────────────────────────────────────────────────────────
A multi-agent system that uses a **routing pattern** to direct user
queries to the appropriate specialized agent.  The system has:

  - Product QnA Agent  (from Example 8): Answers product feature and
    pricing questions using RAG + pricing tools
  - Orders Agent       (from Example 9): Queries and updates laptop
    orders using custom tools
  - Router Agent:      Classifies each user message and routes to
    the correct specialist or handles small talk directly

Key concepts demonstrated:
  - Multi-agent composition: Reusing existing agents as nodes in a
    larger orchestration graph
  - Routing pattern: An LLM-based classifier that inspects each
    query and forwards it to the right agent
  - Agent-as-node: functools.partial wraps each sub-agent invocation
    so it can be used as a graph node
  - Separation of concerns: Each agent handles one domain; the router
    handles orchestration and small talk

Graph design:
  START → Router → [find_route] → Product_Agent  → END
                                 → Orders_Agent   → END
                                 → Small_Talk      → END
                                 → END (fallback)

See also: README_MULTI_AGENT_ROUTER.md for architecture diagram and design doc.
"""

import functools
import uuid
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.messages import (
    AIMessage, AnyMessage, SystemMessage, HumanMessage, ToolMessage,
)
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
import operator

load_dotenv()

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PRICING_CSV = DATA_DIR / "laptop_pricing.csv"
DESCRIPTIONS_FILE = DATA_DIR / "laptop_descriptions.txt"
ORDERS_CSV = DATA_DIR / "laptop_orders.csv"


# ─── 1. Setup LLM ────────────────────────────────────────────────────────────
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedding = OpenAIEmbeddings(model="text-embedding-3-small")


# ─── 2. Build Product QnA Agent (from Example 8) ─────────────────────────────
# The Product QnA agent uses two tools:
#   get_laptop_price    — CSV lookup for pricing
#   get_product_features — RAG retrieval for specs/features

product_pricing_df = pd.read_csv(PRICING_CSV)


@tool
def get_laptop_price(laptop_name: str) -> int:
    """
    Return the price of a laptop given its name.
    Performs a substring match (case-insensitive). Returns -1 if not found.
    """
    match_records = product_pricing_df[
        product_pricing_df["Name"].str.contains(
            "^" + laptop_name, case=False, regex=True
        )
    ]
    if len(match_records) == 0:
        return -1
    return int(match_records["Price"].iloc[0])


loader = TextLoader(str(DESCRIPTIONS_FILE), encoding="utf-8")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)
splits = text_splitter.split_documents(docs)
prod_feature_store = Chroma.from_documents(documents=splits, embedding=embedding)

get_product_features = create_retriever_tool(
    prod_feature_store.as_retriever(search_kwargs={"k": 2}),
    name="get_product_features",
    description="""Search for laptop product features and specifications.
    Use when asked about: laptop features, specs, CPU, memory, storage, design,
    or which laptops are available. Returns descriptions of matching laptops.""",
)

product_qna_system = SystemMessage(
    content="""\
You are a professional chatbot that answers questions about laptops sold by your company.
To answer questions about laptops, you will ONLY use the available tools and NOT your own memory.
For product names, features, or pricing — always call the appropriate tool first.
You will handle small talk and greetings with professional, friendly responses."""
)

product_qna_agent = create_react_agent(
    model=model,
    tools=[get_laptop_price, get_product_features],
    state_modifier=product_qna_system,
    checkpointer=MemorySaver(),
)


# ─── 3. Build Orders Agent (from Example 9) ──────────────────────────────────
# The Orders agent uses two tools:
#   get_order_details — READ order info
#   update_quantity   — WRITE order quantity

product_orders_df = pd.read_csv(ORDERS_CSV)


@tool
def get_order_details(order_id: str) -> str:
    """
    Return details about a laptop order given an order ID.
    Exact match on Order ID. Returns -1 if not found.
    """
    match_order_df = product_orders_df[
        product_orders_df["Order ID"] == order_id
    ]
    if len(match_order_df) == 0:
        return -1
    return match_order_df.iloc[0].to_dict()


@tool
def update_quantity(order_id: str, new_quantity: int) -> bool:
    """
    Update the quantity of laptops ordered for a given order ID.
    Returns True if updated, False if order not found.
    """
    global product_orders_df
    match_order_df = product_orders_df[
        product_orders_df["Order ID"] == order_id
    ]
    if len(match_order_df) == 0:
        return False
    product_orders_df.loc[
        product_orders_df["Order ID"] == order_id,
        "Quantity Ordered",
    ] = new_quantity
    return True


class OrdersAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class OrdersAgent:
    """Manually-built ReAct agent for order management (from Example 9)."""

    def __init__(self, model, tools, system_prompt, debug=False):
        self.system_prompt = system_prompt
        self.debug = debug

        agent_graph = StateGraph(OrdersAgentState)
        agent_graph.add_node("orders_llm", self.call_llm)
        agent_graph.add_node("orders_tools", self.call_tools)
        agent_graph.add_conditional_edges(
            "orders_llm",
            self.is_tool_call,
            {True: "orders_tools", False: END},
        )
        agent_graph.add_edge("orders_tools", "orders_llm")
        agent_graph.set_entry_point("orders_llm")
        self.memory = MemorySaver()
        self.agent_graph = agent_graph.compile(checkpointer=self.memory)
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def call_llm(self, state: OrdersAgentState):
        messages = state["messages"]
        if self.system_prompt:
            messages = [SystemMessage(content=self.system_prompt)] + messages
        result = self.model.invoke(messages)
        if self.debug:
            print(f"\nLLM returned: {result}")
        return {"messages": [result]}

    def is_tool_call(self, state: OrdersAgentState):
        return len(state["messages"][-1].tool_calls) > 0

    def call_tools(self, state: OrdersAgentState):
        tool_calls = state["messages"][-1].tool_calls
        results = []
        for tc in tool_calls:
            if tc["name"] not in self.tools:
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


ORDERS_SYSTEM_PROMPT = """\
You are a professional chatbot that manages orders for laptops sold by our company.
The tools allow for retrieving order details as well as updating order quantity.
Do NOT reveal information about other orders than the one requested.
You will handle small talk and greetings by producing professional responses."""

orders_agent = OrdersAgent(
    model,
    [get_order_details, update_quantity],
    ORDERS_SYSTEM_PROMPT,
    debug=False,
)


# ─── 4. Agent Node Helper ────────────────────────────────────────────────────
# Wraps a sub-agent so it can be used as a node in the router graph.
# Extracts thread_id from config metadata so each sub-agent keeps
# its own conversation memory.

def agent_node(state, agent, name, config):
    thread_id = config["metadata"]["thread_id"]
    agent_config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(state, agent_config)
    if not isinstance(result, ToolMessage):
        final_result = AIMessage(result["messages"][-1].content)
    else:
        final_result = result
    return {"messages": [final_result]}


product_qna_node = functools.partial(
    agent_node, agent=product_qna_agent, name="Product_QnA_Agent"
)
orders_node = functools.partial(
    agent_node, agent=orders_agent.agent_graph, name="Orders_Agent"
)


# ─── 5. RouterAgent Class ────────────────────────────────────────────────────
# The Router classifies each user message into one of four categories:
#   PRODUCT   → route to Product QnA Agent
#   ORDER     → route to Orders Agent
#   SMALLTALK → handle with a small-talk prompt
#   END       → fallback, end the graph

class RouterAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class RouterAgent:

    def __init__(self, model, system_prompt, smalltalk_prompt, debug=False):
        self.system_prompt = system_prompt
        self.smalltalk_prompt = smalltalk_prompt
        self.model = model
        self.debug = debug

        router_graph = StateGraph(RouterAgentState)
        router_graph.add_node("Router", self.call_llm)
        router_graph.add_node("Product_Agent", product_qna_node)
        router_graph.add_node("Orders_Agent", orders_node)
        router_graph.add_node("Small_Talk", self.respond_smalltalk)

        router_graph.add_conditional_edges(
            "Router",
            self.find_route,
            {
                "PRODUCT": "Product_Agent",
                "ORDER": "Orders_Agent",
                "SMALLTALK": "Small_Talk",
                "END": END,
            },
        )

        router_graph.add_edge("Product_Agent", END)
        router_graph.add_edge("Orders_Agent", END)
        router_graph.add_edge("Small_Talk", END)
        router_graph.set_entry_point("Router")
        self.router_graph = router_graph.compile()

    def call_llm(self, state: RouterAgentState):
        messages = state["messages"]
        if self.debug:
            print(f"Router received: {messages}")
        if self.system_prompt:
            messages = [SystemMessage(content=self.system_prompt)] + messages
        result = self.model.invoke(messages)
        if self.debug:
            print(f"Router classified: {result}")
        return {"messages": [result]}

    def respond_smalltalk(self, state: RouterAgentState):
        messages = state["messages"]
        if self.debug:
            print(f"Small talk received: {messages}")
        messages = [SystemMessage(content=self.smalltalk_prompt)] + messages
        result = self.model.invoke(messages)
        if self.debug:
            print(f"Small talk result: {result}")
        return {"messages": [result]}

    def find_route(self, state: RouterAgentState):
        last_message = state["messages"][-1]
        if self.debug:
            print(f"Router decision: {last_message.content}")
        return last_message.content.strip()


# ─── 6. Create the Router Agent ──────────────────────────────────────────────

ROUTER_SYSTEM_PROMPT = """\
You are a Router that analyzes the input query and chooses one of 4 options:
SMALLTALK: If the user input is small talk, like greetings and goodbyes.
PRODUCT: If the query is a product question about laptops, like features, specifications and pricing.
ORDER: If the query is about orders for laptops, like order status, order details or update order quantity.
END: Default, when it is neither PRODUCT nor ORDER nor SMALLTALK.

The output should be ONLY one word: SMALLTALK, PRODUCT, ORDER, or END."""

SMALLTALK_PROMPT = """\
If the user request is small talk, like greetings and goodbyes, respond professionally.
Mention that you will be able to answer questions about laptop product features and \
provide order status and updates."""

router_agent = RouterAgent(
    model,
    ROUTER_SYSTEM_PROMPT,
    SMALLTALK_PROMPT,
    debug=False,
)


# ─── 7. Run Examples ─────────────────────────────────────────────────────────

def run_single_queries():
    """Single queries routed to different agents."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())},
              "metadata": {"thread_id": str(uuid.uuid4())}}

    print("=" * 60)
    print("Test 1: Product query → routes to Product Agent")
    print("=" * 60)
    messages = [HumanMessage(content="Tell me about the features of SpectraBook")]
    result = router_agent.router_graph.invoke({"messages": messages}, config)
    for message in result["messages"]:
        print(message.pretty_repr())

    print("\n" + "=" * 60)
    print("Test 2: Order query → routes to Orders Agent")
    print("=" * 60)
    config = {"configurable": {"thread_id": str(uuid.uuid4())},
              "metadata": {"thread_id": str(uuid.uuid4())}}
    messages = [HumanMessage(content="What is the status of order ORD-7311?")]
    result = router_agent.router_graph.invoke({"messages": messages}, config)
    for message in result["messages"]:
        print(message.pretty_repr())


def run_multi_turn_conversation():
    """
    Multi-turn conversation that spans multiple domains.

    Demonstrates:
      - Small talk ("How are you doing?") → Small_Talk node
      - Order query ("details of ORD-7311") → Orders Agent
      - Order update ("add one more") → Orders Agent (with memory)
      - Product query ("features of SpectraBook") → Product Agent
      - Product follow-up ("How much does it cost?") → Product Agent (with memory)
      - Farewell ("Bye") → Small_Talk node
    """
    user_inputs = [
        "How are you doing?",
        "Please show me the details of the order ORD-7311",
        "Can you add one more of that laptop to the order?",
        "Tell me about the features of SpectraBook laptop",
        "How much does it cost?",
        "Bye",
    ]

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id},
              "metadata": {"thread_id": thread_id}}

    for user_input in user_inputs:
        print(f"{'─' * 40}\nUSER  : {user_input}")
        user_message = {"messages": [HumanMessage(user_input)]}
        ai_response = router_agent.router_graph.invoke(user_message, config=config)
        print(f"AGENT : {ai_response['messages'][-1].content}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Multi-Agent Router — Single Queries")
    print("=" * 60)
    run_single_queries()

    print("\n\n")
    print("=" * 60)
    print("Multi-Agent Router — Multi-Turn Conversation")
    print("=" * 60)
    run_multi_turn_conversation()
