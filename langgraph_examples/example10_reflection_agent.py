# file: langgraph_examples/example10_reflection_agent.py
"""
Reflection-Based Summary Agent
──────────────────────────────
A summarizer chatbot that uses the **reflection pattern** to iteratively
improve a summary of an input document.  Unlike tool-use or planning
patterns, reflection lets one LLM node (the summarizer) generate output
while a second LLM node (the reviewer) critiques it, feeding the
critique back so the summarizer can revise.

Key concepts demonstrated:
  - Reflection pattern: Generate → Review → Revise loop
  - Custom StateGraph with conditional edges (no tool use)
  - SummaryAgent class: Encapsulates graph, prompts, and memory
  - MemorySaver: Conversation memory per thread_id — the user can
    ask follow-up questions like "focus more on the specs"
  - Iteration control: The conditional edge caps the generate/review
    loop at a configurable number of iterations

Graph design:
  START → summarizer → [should_continue?] → reviewer (yes) → summarizer
                                           → END (no — summary is ready)

See also: README_REFLECTION_AGENT.md for architecture diagram and design doc.
"""

import uuid
from pathlib import Path

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
import operator

load_dotenv()

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SPEC_FILE = DATA_DIR / "ecosprint_specification.txt"


# ─── 1. Setup LLM ────────────────────────────────────────────────────────────
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─── 2. Engineer Prompts for Reflection ───────────────────────────────────────

SUMMARIZER_PROMPT = """\
You are a document summarizer who can summarize a document provided to you.
For the input provided, create a summary with less than 50 words.
If the user has provided critique, respond with a revised version of your \
previous attempts incorporating the feedback."""

REVIEWER_PROMPT = """\
You are a reviewer grading summaries for an article.
Compare the user input document and the generated summary.
Check if the summary accurately reflects the contents of the document.
Provide recommendations for improvement in less than 50 words."""


# ─── 3. Agent State ──────────────────────────────────────────────────────────
# The agent state accumulates all messages (user input, summaries, reviews).
# `operator.add` means new messages are APPENDED, preserving the full history
# so the summarizer can see the reviewer's feedback and vice versa.

class SummaryAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


# ─── 4. SummaryAgent Class ───────────────────────────────────────────────────
# Encapsulates the reflection loop: summarizer ↔ reviewer with a cap on
# iterations controlled by the should_continue conditional edge.

class SummaryAgent:

    def __init__(self, model, summarizer_prompt, reviewer_prompt,
                 max_iterations=3, debug=False):
        """
        Build the reflection agent graph.

        Parameters:
          model             — A LangChain chat model (e.g., ChatOpenAI)
          summarizer_prompt — System prompt for the summarizer node
          reviewer_prompt   — System prompt for the reviewer node
          max_iterations    — Maximum generate/review cycles before returning
          debug             — If True, prints intermediate outputs
        """
        self.model = model
        self.summarizer_prompt = summarizer_prompt
        self.reviewer_prompt = reviewer_prompt
        self.max_iterations = max_iterations
        self.debug = debug

        # --- Build the graph ---
        graph = StateGraph(SummaryAgentState)

        graph.add_node("summarizer", self.generate_summary)
        graph.add_node("reviewer", self.review_summary)

        # Conditional edge: after the summarizer runs, decide whether to
        # continue (route to reviewer) or stop (route to END).
        graph.add_conditional_edges(
            "summarizer",
            self.should_continue,
            {True: "reviewer", False: END}
        )

        # After the reviewer runs, always loop back to the summarizer
        # so it can incorporate the feedback.
        graph.add_edge("reviewer", "summarizer")

        graph.set_entry_point("summarizer")

        self.memory = MemorySaver()
        self.graph = graph.compile(checkpointer=self.memory)

    def generate_summary(self, state: SummaryAgentState):
        """
        Summarizer node: Generates or revises a summary.

        On the first call the messages contain only the user's document.
        On subsequent calls they also contain previous summaries and
        reviewer feedback, so the LLM can refine its output.
        """
        messages = [SystemMessage(content=self.summarizer_prompt)] + state["messages"]
        result = self.model.invoke(messages)

        if self.debug:
            print(f"{'=' * 50}\nSummarizer output:\n{result.content}\n")
        return {"messages": [result]}

    def review_summary(self, state: SummaryAgentState):
        """
        Reviewer node: Critiques the current summary.

        Receives the full message history (original document + summaries +
        previous reviews) and produces improvement recommendations.
        """
        messages = [SystemMessage(content=self.reviewer_prompt)] + state["messages"]
        result = self.model.invoke(messages)

        if self.debug:
            print(f"{'*' * 50}\nReviewer output:\n{result.content}\n")
        return {"messages": [result]}

    def should_continue(self, state: SummaryAgentState):
        """
        Conditional edge: Caps the reflection loop.

        Each iteration adds 2 messages (one from summarizer, one from reviewer).
        The first message is the user input, so after N iterations the total
        message count is 1 + 2*N.  We stop when N >= max_iterations.
        """
        total_iterations = len(state["messages"]) // 2

        if self.debug:
            print(f"Iteration: {total_iterations} / {self.max_iterations}")

        return total_iterations < self.max_iterations


# ─── 5. Load the Source Document ──────────────────────────────────────────────

source_content = SPEC_FILE.read_text().strip()


# ─── 6. Create the Summary Agent ─────────────────────────────────────────────

summary_agent = SummaryAgent(
    model,
    SUMMARIZER_PROMPT,
    REVIEWER_PROMPT,
    max_iterations=3,
    debug=False,
)


# ─── 7. Run Examples ─────────────────────────────────────────────────────────

def run_single_summary():
    """
    Runs the reflection loop once with debug ON to show the
    generate → review → revise cycle in action.
    """
    debug_agent = SummaryAgent(
        model,
        SUMMARIZER_PROMPT,
        REVIEWER_PROMPT,
        max_iterations=3,
        debug=True,
    )

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    messages = [HumanMessage(content=source_content)]
    result = debug_agent.graph.invoke({"messages": messages}, config)

    print(f"\n{'=' * 60}")
    print("Final summary after reflection:")
    print(f"{'=' * 60}")
    print(result["messages"][-1].content)


def run_interactive_conversation():
    """
    Multi-turn conversation: the user can provide follow-up feedback
    on the summary (e.g., "focus more on specs", "remove touchscreen
    details"). Each turn triggers a fresh reflection loop, but the
    conversation memory preserves context across turns.
    """
    user_inputs = [
        source_content,
        "Can you rewrite the summary by focusing more on the specifications?",
        "Can you remove details about the touchscreen?",
    ]

    config = {"configurable": {"thread_id": "thread-summarizer"}}

    for user_input in user_inputs:
        display = user_input[:80] + "..." if len(user_input) > 80 else user_input
        print(f"{'─' * 40}\nUSER  : {display}")
        user_message = {"messages": [HumanMessage(content=user_input)]}
        ai_response = summary_agent.graph.invoke(user_message, config=config)
        print(f"AGENT : {ai_response['messages'][-1].content}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Reflection Agent — Single Summary (debug mode)")
    print("=" * 60)
    run_single_summary()

    print("\n\n")
    print("=" * 60)
    print("Reflection Agent — Interactive Conversation")
    print("=" * 60)
    run_interactive_conversation()
