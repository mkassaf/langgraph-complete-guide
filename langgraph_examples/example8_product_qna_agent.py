# file: langgraph_examples/example8_product_qna_agent.py
"""
Product QnA Chatbot — RAG + Pricing Tools + Conversation Memory
───────────────────────────────────────────────────────────────
A ReAct agent that answers questions about laptops using:
  1. get_laptop_price — Looks up price from a CSV (exact/substring match)
  2. get_product_features — RAG over product descriptions (Chroma + embeddings)

Key concepts demonstrated:
  - create_react_agent: One-liner ReAct agent with tools
  - MemorySaver (checkpointer): Conversation memory across turns — each thread_id
    keeps its own history so "How much does it cost?" refers to the last laptop discussed
  - create_retriever_tool: Wraps a vector-store retriever as a tool the LLM can call
  - Multi-user: Different thread_ids = different conversations; each user gets
    their own context (USER 1 asked about SpectraBook, USER 2 about GammaAir)

Flow: User asks → Agent reasons → Calls get_laptop_price and/or get_product_features
→ Gets results → Agent synthesizes answer. With checkpointer, full history is passed
so follow-up questions like "What is its price?" work correctly.
"""

import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

import pandas as pd

load_dotenv()

# ─── Paths ───────────────────────────────────────────────────────────────────
# Resolve paths relative to project root (parent of langgraph_examples/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PRICING_CSV = DATA_DIR / "laptop_pricing.csv"
DESCRIPTIONS_FILE = DATA_DIR / "laptop_descriptions.txt"


# ─── 1. Setup LLM and Embeddings ──────────────────────────────────────────────
# ChatOpenAI: The LLM that powers the agent. Uses OPENAI_API_KEY from .env.
# OpenAIEmbeddings: Converts text to vectors for the RAG retriever. Uses the same
# API key. Different models: gpt-4o-mini for chat, text-embedding-3-small for embeddings.
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embedding = OpenAIEmbeddings(model="text-embedding-3-small")


# ─── 2. Product Pricing Tool ─────────────────────────────────────────────────
# Loads a CSV with product names and prices. The tool performs a substring match
# (case-insensitive) so "GammaAir" matches "GammaAir X", "alpha" matches "AlphaBook Pro".
# Returns -1 if no match — the agent can then say "I don't have that product."

product_pricing_df = pd.read_csv(PRICING_CSV)


@tool
def get_laptop_price(laptop_name: str) -> int:
    """
    Return the price of a laptop given its name.
    Performs a substring match (case-insensitive). If the input matches the start
    of a laptop name, returns that laptop's price. Use for pricing questions.
    Returns -1 if no match is found.
    """
    # Filter rows where "Name" starts with the given string (regex: ^laptop_name)
    match_records = product_pricing_df[
        product_pricing_df["Name"].str.contains("^" + laptop_name, case=False, regex=True)
    ]
    if len(match_records) == 0:
        return -1
    return int(match_records["Price"].iloc[0])


# ─── 3. Product Features Retrieval Tool (RAG) ──────────────────────────────────
# RAG = Retrieval-Augmented Generation. We:
# 1. Load product descriptions from a text file
# 2. Split into chunks (overlap helps preserve context at boundaries)
# 3. Embed chunks and store in Chroma (vector DB)
# 4. Create a retriever that finds relevant chunks for a query
# 5. Wrap the retriever as a tool — when the LLM calls it, we get chunks and
#    return them as context for the answer

# Load and chunk documents
loader = TextLoader(str(DESCRIPTIONS_FILE), encoding="utf-8")
docs = loader.load()

# RecursiveCharacterTextSplitter: Splits on \n\n, then \n, then " ", then chars.
# chunk_overlap=256: Adjacent chunks share 256 chars so context isn't lost at boundaries.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)
splits = text_splitter.split_documents(docs)

# Chroma: In-memory vector store. Each chunk is embedded and stored.
# as_retriever(search_kwargs={"k": 2}): Returns top 2 most similar chunks for a query.
prod_feature_store = Chroma.from_documents(documents=splits, embedding=embedding)

# create_retriever_tool: Turns the retriever into a LangChain tool. The LLM receives
# the name and description, and when it calls the tool, we invoke the retriever and
# return the retrieved text as the tool's response.
get_product_features = create_retriever_tool(
    prod_feature_store.as_retriever(search_kwargs={"k": 2}),
    name="get_product_features",
    description="""Search for laptop product features and specifications.
    Use when asked about: laptop features, specs, CPU, memory, storage, design,
    or which laptops are available. Returns descriptions of matching laptops.""",
)


# ─── 4. Create the Product QnA Agent ─────────────────────────────────────────
# System prompt: Defines the agent's persona. "Use ONLY tools" prevents hallucination
# — the agent must call get_laptop_price or get_product_features for product info.
# "Handle small talk" — for "Hello" or "Thanks" it can respond without tools.

system_prompt = SystemMessage(content="""You are a professional chatbot that answers questions about laptops sold by your company.
To answer questions about laptops, you will ONLY use the available tools and NOT your own memory.
For product names, features, or pricing — always call the appropriate tool first.
You will handle small talk and greetings with professional, friendly responses.""")

tools = [get_laptop_price, get_product_features]

# MemorySaver: Checkpointer that stores conversation state in memory.
# Each thread_id gets its own history. When we invoke with config={"configurable": {"thread_id": "user-1"}},
# the agent sees all previous messages in that thread. So "How much does it cost?" (after
# discussing SpectraBook) correctly refers to SpectraBook.
checkpointer = MemorySaver()

product_qna_agent = create_react_agent(
    model=model,
    tools=tools,
    state_modifier=system_prompt,
    checkpointer=checkpointer,
    debug=False,
)


# ─── 5. Run Examples ────────────────────────────────────────────────────────
def run_single_query():
    """Single query: features + pricing for one laptop. Uses stream() to see progress."""
    print("=" * 60)
    print("Example 1: Single query (features + pricing)")
    print("=" * 60)

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    inputs = {"messages": [HumanMessage(content="What are the features and pricing for GammaAir?")]}

    # stream() with stream_mode="values": Yields full state after each step.
    # message.pretty_print(): Prints HumanMessage, AIMessage (with tool_calls), ToolMessage, etc.
    for stream in product_qna_agent.stream(inputs, config, stream_mode="values"):
        message = stream["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


def run_multi_turn_conversation():
    """Multi-turn: Simulates a conversation. Same thread_id = conversation memory."""
    print("\n" + "=" * 60)
    print("Example 2: Multi-turn conversation (memory enabled)")
    print("=" * 60)

    user_inputs = [
        "Hello",
        "I am looking to buy a laptop",
        "Give me a list of available laptop names",
        "Tell me about the features of SpectraBook",
        "How much does it cost?",  # Refers to SpectraBook — memory!
        "Give me similar information about OmegaPro",
        "What info do you have on AcmeRight?",  # Not in catalog — agent says so
        "Thanks for the help",
    ]

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    for user_input in user_inputs:
        print(f"\n{'─' * 40}\nUSER : {user_input}")
        result = product_qna_agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
        )
        print(f"AGENT : {result['messages'][-1].content}")


def run_multi_user():
    """Multi-user: Different thread_ids = separate conversations. Each user's
    'it' or 'its price' refers to the laptop they asked about."""
    print("\n" + "=" * 60)
    print("Example 3: Multi-user (separate conversation memory per user)")
    print("=" * 60)

    def ask(user_label: str, config: dict, prompt: str):
        result = product_qna_agent.invoke(
            {"messages": [HumanMessage(content=prompt)]},
            config=config,
        )
        print(f"\n{user_label}: {result['messages'][-1].content}")

    config_1 = {"configurable": {"thread_id": str(uuid.uuid4())}}
    config_2 = {"configurable": {"thread_id": str(uuid.uuid4())}}

    # USER 1 asks about SpectraBook, USER 2 about GammaAir
    ask("USER 1", config_1, "Tell me about the features of SpectraBook")
    ask("USER 2", config_2, "Tell me about the features of GammaAir")
    # "its price" — USER 1 gets SpectraBook price, USER 2 gets GammaAir price
    ask("USER 1", config_1, "What is its price?")
    ask("USER 2", config_2, "What is its price?")


if __name__ == "__main__":
    run_single_query()
    run_multi_turn_conversation()
    run_multi_user()
