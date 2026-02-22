# file: langchain_example2_prompts.py
# Example 2 — Prompt Templates

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Create a template with placeholders
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Answer briefly and clearly."),
    ("human", "{question}")
])

# Fill in the variables
messages = prompt.format_messages(role="math tutor", question="What is 15% of 80?")
response = llm.invoke(messages)

print(response.content)
