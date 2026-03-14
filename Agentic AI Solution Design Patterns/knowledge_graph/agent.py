"""
Knowledge Graph — Office Building Agent

Compares answers with and without knowledge graph.
"""

from config import MODEL, MAX_TOKENS
from llm_client import LLMClient
from controller import Controller, AgentResponse
from graph.graph_builder import GraphBuilder
from graph.graph_query_tool import GraphQueryTool


TEST_QUESTIONS = [
    "Where is the printer located?",
    "What paper does the printer use and where is it stored?",
    "Who should I contact if the printer breaks?",
    "What equipment is available in room 303?",
    "How do I get from the printer to the paper supply?",
]


class OfficeBuildingAgent:
    def __init__(self):
        self.llm = LLMClient(model=MODEL, max_tokens=MAX_TOKENS)
        self.controller = Controller(self.llm)
        graph_builder = GraphBuilder()
        self.graph = graph_builder.build_office_graph()
        self.graph = graph_builder.simulate_recent_change(self.graph)
        self.graph_tool = GraphQueryTool(self.graph)

    def run_comparison(self) -> list[tuple[AgentResponse, AgentResponse]]:
        """For each test question, run both modes and return pairs."""
        results = []
        for q in TEST_QUESTIONS:
            without = self.controller.answer_without_graph(q)
            with_kg = self.controller.answer_with_graph(q, self.graph_tool)

            # Graph ground truth for printer location
            graph_truth = with_kg.graph_data_used or ""
            without.is_hallucination = self.controller.detect_hallucination(
                without.llm_answer, graph_truth
            )
            with_kg.correct_answer = graph_truth

            results.append((without, with_kg))
        return results
