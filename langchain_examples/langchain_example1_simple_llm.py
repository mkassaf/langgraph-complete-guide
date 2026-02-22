# file: langchain_examples/langchain_example1_simple_llm.py
# Example 1 — Simple LLM Call (No Prompts, No Chains)

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Option A: Plain string (treated as user message)
print("--- Option A: Plain string ---")
response = llm.invoke("What is the capital of France?")
print(response.content)

# Option B: Explicit messages (for system + user)
print("\n--- Option B: System + Human messages ---")
messages = [
    SystemMessage(content="You are a concise geography tutor."),
    HumanMessage(content="What is the capital of France?")
]
response = llm.invoke(messages)
print(response.content)
