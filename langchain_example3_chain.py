# file: langchain_example3_chain.py
# Example 3 — LCEL Chains (Pipe Your Steps)

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Be concise."),
    ("human", "{question}")
])

# Chain: prompt | llm | parser
# The parser converts the LLM's AIMessage to a plain string
parser = StrOutputParser()
chain = prompt | llm | parser

# Invoke with a dict of template variables
result = chain.invoke({
    "role": "research assistant",
    "question": "What is a transformer in NLP?"
})
print(result)
