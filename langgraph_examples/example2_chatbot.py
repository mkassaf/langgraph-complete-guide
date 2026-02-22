# file: langgraph_examples/example2_chatbot.py

# ─── Imports ─────────────────────────────────────────────────────────────────
import os
from dotenv import load_dotenv

# LangChain components for talking to OpenAI
from langchain_core.runnables.config import P
from langchain_openai import ChatOpenAI

# LangGraph components
from langgraph.graph import StateGraph, MessagesState, START, END

# LangChain message types
from langchain_core.messages import HumanMessage, SystemMessage

# ─── Load API Key ─────────────────────────────────────────────────────────────
load_dotenv()  # Reads your .env file and sets environment variables
# Now os.environ["OPENAI_API_KEY"] is automatically set

# ─── Understanding MessagesState ──────────────────────────────────────────────
# MessagesState is a built-in state type provided by LangGraph.
# It looks roughly like this:
#
#   class MessagesState(TypedDict):
#       messages: Annotated[list[AnyMessage], add_messages]
#
# The "add_messages" annotation is special — it tells LangGraph to APPEND
# new messages to the list instead of replacing the whole list.
# This is how conversation history is maintained automatically.

# ─── Set Up the LLM ───────────────────────────────────────────────────────────
# ChatOpenAI is a LangChain wrapper around OpenAI's chat API
llm = ChatOpenAI(
    model="gpt-4o-mini",   # A fast, cheap model — good for testing
    temperature=1.0,        # 0 = deterministic, 1 = creative. 0.7 is balanced
)

# ─── Define the Node ──────────────────────────────────────────────────────────
def chatbot_node(state: MessagesState) -> dict:
    """
    This node:
    1. Reads all messages from the state (conversation history)
    2. Sends them to the LLM
    3. Gets a response
    4. Returns the response as a new message to be added to history
    """
    # state["messages"] is a list of all messages so far
    # We prepend a system message to set the assistant's personality
    system_msg = SystemMessage(content="""
    You are a helpful research assistant for a PhD student.
    Be concise, precise, and always cite when you're uncertain.
    """)
    
    # Build the full message list: [system] + [all previous messages]
    all_messages = [system_msg] + state["messages"]
    
    print("===================  Message Start ============================")
    print(all_messages)
    print("===================  Message End ============================")
    # Call the LLM with the full conversation
    response = llm.invoke(all_messages)
    
    # Return the AI's response — it will be APPENDED to messages automatically
    # because of the add_messages annotation in MessagesState
    return {"messages": [response]}

# ─── Build the Graph ──────────────────────────────────────────────────────────
graph = StateGraph(MessagesState)

graph.add_node("chatbot", chatbot_node)

graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

app = graph.compile()

# ─── Run as a Multi-Turn Conversation ─────────────────────────────────────────
print("Simple Research Assistant Chatbot")
print("Type 'quit' to exit\n")

# We maintain the conversation history ourselves across turns
conversation_history = []

while True:
    user_input = input("You: ").strip()
    
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    
    if not user_input:
        continue
    
    # Add the user's message to history
    conversation_history.append(HumanMessage(content=user_input))
    
    # Run the graph with the full conversation history
    result = app.invoke({"messages": conversation_history})
    
    # result["messages"] now contains the full history including the new AI response
    # The last message is the AI's response
    ai_response = result["messages"][-1]
    
    print(f"Assistant: {ai_response.content}\n")
    
    # Update our history with the result (includes the AI response now)
    conversation_history = result["messages"]