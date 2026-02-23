# file: langgraph_examples/example5_research_pipeline.py
"""
Research Multi-Agent Pipeline (Full System)
───────────────────────────────────────────
A sequential pipeline of specialized agents that collaborate on a research task:
Planner → Searcher → Analyzer → Writer. Unlike the supervisor pattern (Example 4),
this is a fixed linear flow — no conditional routing, no loops.

Architecture:
    START → planner → searcher → analyzer → writer → END

Each agent reads from and writes to a shared ResearchState. Key difference from
MessagesState: we use structured fields (subtasks, literature_findings, analysis,
final_report) instead of a message list. Annotated[List[str], add] means list
fields are APPENDED when multiple nodes return updates (not overwritten).

Flow:
  1. Planner: Breaks research question into 3-4 subtasks (specific questions).
  2. Searcher: For each subtask, calls search_arxiv tool, summarizes findings.
  3. Analyzer: Synthesizes all findings, identifies gaps and themes.
  4. Writer: Produces a polished research summary report.
"""

import os
from typing import TypedDict, Annotated, List, Optional
from operator import add  # Used by Annotated[List, add] for list concatenation
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# ─── Rich State for Research Pipeline ─────────────────────────────────────────
# Unlike MessagesState (message list), we use structured fields. Each agent reads
# what it needs and writes to its designated fields. Annotated[List[str], add]
# uses operator.add as reducer: when a node returns {"subtasks": ["a","b"]},
# LangGraph does state["subtasks"] = state["subtasks"] + ["a","b"] (append, not replace).

class ResearchState(TypedDict):
    research_question: str       # Original question; read by all agents
    subtasks: Annotated[List[str], add]           # Planner writes; Searcher reads
    literature_findings: Annotated[List[str], add]  # Searcher writes; Analyzer reads
    analysis: str                # Analyzer writes; Writer reads
    final_report: str            # Writer writes; final output
    current_step: str            # For monitoring/debugging which step completed

# ─── Tools ────────────────────────────────────────────────────────────────────

@tool
def search_arxiv(query: str) -> str:
    """
    Search ArXiv for recent papers on a topic.
    Returns titles, authors, and abstracts of relevant papers.
    """
    # In production: use the ArXiv API (pip install arxiv)
    # import arxiv
    # search = arxiv.Search(query=query, max_results=5)
    # return "\n".join([f"{r.title}: {r.summary[:200]}" for r in search.results()])
    
    # Mock response for this tutorial
    mock_responses = {
        "large language model": """
            Found 3 papers:
            1. "GPT-4 Technical Report" (OpenAI, 2023) - Describes GPT-4's capabilities and training.
            2. "Llama 2" (Touvron et al., 2023) - Open-source LLM with 70B parameters.
            3. "Mistral 7B" (Jiang et al., 2023) - Efficient 7B model outperforming larger models.
        """,
        "hallucination": """
            Found 3 papers:
            1. "TruthfulQA" (Lin et al., 2022) - Benchmark measuring LLM truthfulness.
            2. "Self-RAG" (Asai et al., 2023) - Model learns to retrieve and reflect.
            3. "Chain-of-Verification" (Dhuliawala et al., 2023) - LLM verifies its own answers.
        """,
    }
    
    for keyword, result in mock_responses.items():
        if keyword in query.lower():
            return result
    return f"Found limited results for '{query}'. Key papers may require specialized database access."

@tool
def analyze_gap(findings: str) -> str:
    """
    Analyze research findings to identify gaps and research opportunities.
    Input: a summary of literature findings.
    Output: identified research gaps and suggested directions.
    """
    return f"""Research Gap Analysis:
    Based on the provided findings, key gaps include:
    1. Lack of standardized evaluation benchmarks
    2. Limited cross-domain generalization studies  
    3. Computational efficiency in real-world deployment
    4. Long-term impact and societal implications need further study
    
    Suggested research directions:
    - Develop unified evaluation frameworks
    - Study domain adaptation techniques
    - Investigate model compression without capability loss
    """

# ─── Agent Nodes ──────────────────────────────────────────────────────────────

def planner_agent(state: ResearchState) -> dict:
    """
    Breaks the research question into 3-4 specific subtasks (investigable questions).
    Runs once at the start. Returns subtasks list; LangGraph appends via add reducer.
    """
    print(f"\n[PLANNER] Planning research for: {state['research_question']}")
    
    prompt = f"""You are a research planner. Break this research question into 3-4 specific subtasks:
    
    Research Question: {state['research_question']}
    
    Return ONLY a numbered list of subtasks. Each subtask should be a specific question to investigate.
    Example format:
    1. What are the current state-of-the-art methods for X?
    2. What are the key limitations of existing approaches?
    3. What evaluation metrics are used in this domain?
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Parse LLM output: extract lines that start with a number (1. 2. 3. ...)
    lines = response.content.strip().split("\n")
    subtasks = [line.strip() for line in lines
                if line.strip() and line.strip()[0].isdigit()]
    
    print(f"[PLANNER] Created {len(subtasks)} subtasks")
    for i, task in enumerate(subtasks, 1):
        print(f"  {i}. {task}")
    
    return {
        "subtasks": subtasks,
        "current_step": "planning_complete"
    }

def search_agent(state: ResearchState) -> dict:
    """
    For each subtask, invokes search_arxiv (via bind_tools), executes the tool
    if the LLM calls it, then synthesizes findings. We manually handle the
    tool-call loop here instead of using ToolNode (simpler for one-shot search).
    """
    print(f"\n[SEARCH AGENT] Searching literature for {len(state['subtasks'])} subtasks")
    
    all_findings = []
    
    for i, subtask in enumerate(state["subtasks"], 1):
        print(f"  Searching subtask {i}: {subtask[:60]}...")
        
        prompt = f"""You are a research search agent. Search for information about:
        
        Subtask: {subtask}
        
        Use the search_arxiv tool to find relevant papers, then summarize the findings.
        Context - Overall research question: {state['research_question']}
        """
        
        # Bind search_arxiv so the LLM can choose to call it
        search_llm = llm.bind_tools([search_arxiv])
        response = search_llm.invoke([HumanMessage(content=prompt)])

        # Manual tool execution: if LLM returned tool_calls, run the tool
        # (Alternative: use ToolNode + tools_condition like Example 3, but that
        # would require a subgraph; here we keep it inline for clarity.)
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]
            search_result = search_arxiv.invoke(tool_call['args'])
            
            # Now synthesize the result
            synthesis = llm.invoke([
                HumanMessage(content=f"Subtask: {subtask}\nSearch results: {search_result}\nSummarize the key findings in 2-3 sentences.")
            ])
            finding = f"Subtask: {subtask}\nFindings: {synthesis.content}"
        else:
            finding = f"Subtask: {subtask}\nFindings: {response.content}"
        
        all_findings.append(finding)
    
    print(f"[SEARCH AGENT] Gathered findings for all subtasks")
    
    return {
        "literature_findings": all_findings,
        "current_step": "search_complete"
    }

def analysis_agent(state: ResearchState) -> dict:
    """
    Synthesizes all literature findings into a coherent analysis.
    Also identifies research gaps.
    """
    print(f"\n[ANALYSIS AGENT] Analyzing {len(state['literature_findings'])} sets of findings")
    
    findings_text = "\n\n".join(state["literature_findings"])
    
    prompt = f"""You are a research analysis expert. Synthesize these literature findings:

    Research Question: {state['research_question']}
    
    Literature Findings:
    {findings_text}
    
    Provide:
    1. A synthesis of the current state of knowledge (2-3 paragraphs)
    2. Key themes and patterns across the literature
    3. Identified research gaps and open questions
    4. Methodological considerations for future research
    
    Be specific and academic in tone."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    print(f"[ANALYSIS AGENT] Analysis complete")
    
    return {
        "analysis": response.content,
        "current_step": "analysis_complete"
    }

def writer_agent(state: ResearchState) -> dict:
    """
    Produces the final polished research summary report.
    """
    print(f"\n[WRITER AGENT] Writing final report")
    
    prompt = f"""You are an academic writer. Create a concise but comprehensive research summary.

    Research Question: {state['research_question']}
    
    Analysis: {state['analysis']}
    
    Write a structured research summary with these sections:
    ## Overview
    ## Key Findings
    ## Research Gaps
    ## Recommended Next Steps
    
    Keep it concise (400-600 words). Use academic language.
    This summary will be read by a PhD supervisor."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    print(f"[WRITER AGENT] Report complete")
    
    return {
        "final_report": response.content,
        "current_step": "report_complete"
    }

# ─── Build the Pipeline Graph ─────────────────────────────────────────────────
# Linear flow: no conditional edges, no loops. Each node runs once in order.
# State flows: planner populates subtasks → searcher populates literature_findings
# → analyzer populates analysis → writer populates final_report.

graph = StateGraph(ResearchState)

graph.add_node("planner", planner_agent)
graph.add_node("searcher", search_agent)
graph.add_node("analyzer", analysis_agent)
graph.add_node("writer", writer_agent)

# Linear pipeline: START → planner → searcher → analyzer → writer → END
graph.add_edge(START, "planner")
graph.add_edge("planner", "searcher")
graph.add_edge("searcher", "analyzer")
graph.add_edge("analyzer", "writer")
graph.add_edge("writer", END)

app = graph.compile()

# ─── Run the Research Pipeline ────────────────────────────────────────────────
# Initial state: research_question is set; list fields start empty (planner/searcher
# will populate). LangGraph passes state through each node; each node merges its
# return dict into the state.

research_question = """
What are the current approaches to reducing hallucinations in Large Language Models,
and what are the key open research challenges?
"""

print("=" * 65)
print("RESEARCH PIPELINE STARTING")
print("=" * 65)
print(f"Question: {research_question.strip()}")

result = app.invoke({
    "research_question": research_question,
    "subtasks": [],               # Start empty — planner will populate
    "literature_findings": [],    # Start empty — searcher will populate
    "analysis": "",
    "final_report": "",
    "current_step": "starting"
})

print("\n" + "=" * 65)
print("FINAL RESEARCH REPORT")
print("=" * 65)
print(result["final_report"])

# You can also inspect intermediate results
print("\n" + "=" * 65)
print(f"Subtasks planned: {len(result['subtasks'])}")
print(f"Literature sets found: {len(result['literature_findings'])}")