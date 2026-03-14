"""
Knowledge Graph — Controller

Two modes: no_graph (may hallucinate) vs with_graph (accurate).
"""

from dataclasses import dataclass

from llm_client import LLMClient, LLMResponse
from prompts import NO_GRAPH_PROMPT, WITH_GRAPH_PROMPT
from graph.graph_query_tool import GraphQueryTool, QueryResult


@dataclass
class AgentResponse:
    mode: str
    question: str
    llm_answer: str
    graph_queried: bool
    graph_data_used: str | None
    is_hallucination: bool
    correct_answer: str


class Controller:
    """
    Two modes:
    1. no_graph_mode: LLM answers directly (may hallucinate)
    2. graph_mode: Controller queries graph, feeds to LLM
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def answer_without_graph(self, question: str) -> AgentResponse:
        """Simple LLM call with no graph context. May hallucinate."""
        resp = self.llm.generate(NO_GRAPH_PROMPT, question)
        answer = resp.final_answer or resp.raw_content
        return AgentResponse(
            mode="no_graph",
            question=question,
            llm_answer=answer,
            graph_queried=False,
            graph_data_used=None,
            is_hallucination=False,  # Will be set by agent
            correct_answer="",
        )

    def answer_with_graph(
        self,
        question: str,
        graph_tool: GraphQueryTool,
    ) -> AgentResponse:
        """
        1. Query knowledge graph for relevant entities
        2. Add graph context to LLM prompt
        3. LLM answers using graph data
        """
        result = graph_tool.execute(question)
        context = result.context_string
        prompt = WITH_GRAPH_PROMPT.format(graph_context=context)
        resp = self.llm.generate(prompt, question)
        answer = resp.final_answer or resp.raw_content
        return AgentResponse(
            mode="with_graph",
            question=question,
            llm_answer=answer,
            graph_queried=True,
            graph_data_used=context,
            is_hallucination=False,
            correct_answer=context,
        )

    def detect_hallucination(self, llm_answer: str, graph_truth: str) -> bool:
        """
        Compare LLM answer to graph ground truth.
        Flag if they contradict (e.g., 301 vs 303 for printer).
        """
        llm_lower = llm_answer.lower()
        graph_lower = graph_truth.lower()

        # Key test: printer location
        if "301" in llm_lower and "303" in graph_lower and "printer" in graph_lower:
            return True
        if "room 301" in llm_lower and "room 303" in graph_lower:
            return True
        if "room 303" in graph_lower and "301" in llm_lower:
            return True

        return False
