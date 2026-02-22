# file: langchain_example4_structured_output.py
# Example 4 — Output Parsers & Structured Output

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

load_dotenv()


class ResearchSummary(BaseModel):
    """Structured research summary."""

    key_points: list[str] = Field(description="List of 3 key points")
    conclusion: str = Field(description="One-sentence conclusion")
    confidence: str = Field(description="low, medium, or high")


parser = PydanticOutputParser(pydantic_object=ResearchSummary)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You summarize research topics. Output valid JSON matching this schema:
{format_instructions}""",
    ),
    ("human", "Summarize: {topic}"),
])

chain = prompt | llm | parser
result = chain.invoke({
    "topic": "Large Language Model hallucinations",
    "format_instructions": parser.get_format_instructions(),
})

print("Key points:", result.key_points)
print("Conclusion:", result.conclusion)
print("Confidence:", result.confidence)
