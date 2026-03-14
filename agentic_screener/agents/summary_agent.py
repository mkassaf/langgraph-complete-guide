"""
Summary Agent — Summarizes each paper that is INCLUDED.
Produces a concise 2-3 sentence summary for included papers.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel


SUMMARY_PROMPT = """You are an expert academic paper summarizer. Given a paper's title, authors, and abstract, 
produce a concise 2-3 sentence summary that captures:
1. The main objective or contribution
2. The key method or approach
3. The primary finding or significance

Keep the summary under 100 words. Use precise, academic language. Focus on substance, not filler phrases."""


def summarize_paper(model: BaseChatModel, title: str, authors: str, abstract: str) -> str:
    """
    Generate a summary for an included paper.

    Args:
        model: LLM to use
        title: Paper title
        authors: Author list
        abstract: Paper abstract

    Returns:
        Summary string
    """
    paper_text = f"""Title: {title}
Authors: {authors}
Abstract: {abstract}"""
    messages = [
        SystemMessage(content=SUMMARY_PROMPT),
        HumanMessage(content=paper_text),
    ]
    result = model.invoke(messages)
    return result.content if hasattr(result, 'content') else str(result)
