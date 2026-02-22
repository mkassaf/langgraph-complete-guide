# file: langchain_example6_agent.py
# Example 6 — Agent with Tools (LLM + Tool Binding)

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city. Use when asked about weather."""
    return f"The weather in {city} is sunny, 72°F."


@tool
def add(a: int, b: int) -> int:
    """Add two integers. Use for arithmetic."""
    return a + b


tools = [get_weather, add]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Bind tools to the LLM — now it can choose to call them
llm_with_tools = llm.bind_tools(tools)

# Single invocation — LLM may or may not use tools
response = llm_with_tools.invoke([
    HumanMessage(content="What is 17 + 23? Use a tool if helpful."),
])

print("Content:", response.content)
if response.tool_calls:
    for tc in response.tool_calls:
        print(f"Tool call: {tc['name']}, args: {tc['args']}")
