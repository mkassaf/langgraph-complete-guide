# file: langgraph_examples/example12_paper_screener.py
"""
Systematic Review Paper Screener — Reflection Pattern
──────────────────────────────────────────────────────
An agentic system that screens academic papers for a systematic review.
It reads a CSV of papers, evaluates each against a set of inclusion AND
exclusion criteria using the **reflection pattern**, and outputs a CSV
with INCLUDE/EXCLUDE decisions and per-criterion reasoning.

Decision logic:
  INCLUDE = ALL inclusion criteria are met AND NO exclusion criteria are met
  EXCLUDE = ANY inclusion criterion fails OR ANY exclusion criterion matches

For each paper × each criterion, a reflection loop runs:
  1. Screener — Evaluates the paper against one criterion → PASS/FAIL
  2. Reviewer — Checks if the screener applied the criterion correctly
  3. Screener (revised) — Incorporates reviewer feedback if needed

The per-criterion results are then aggregated into a final decision.

Graph design (per criterion):
  START → screener → [should_continue?] → reviewer (yes) → screener
                                         → END (no — decision is final)

See also: README_PAPER_SCREENER.md for design doc.
"""

import csv
import json
import os
import re
import uuid
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd

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
OUTPUT_DIR = PROJECT_ROOT / "output"
INPUT_CSV = DATA_DIR / "papers.csv"
OUTPUT_CSV = OUTPUT_DIR / "screening_results.csv"


# ─── 1. Setup LLM ────────────────────────────────────────────────────────────
model = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0,
)


# ─── 2. Define Screening Criteria ────────────────────────────────────────────
# Each criterion has:
#   - id:            Short identifier for the CSV column
#   - type:          "inclusion" or "exclusion"
#   - description:   The criterion text
#   - clarification: Optional nuance (e.g., arXiv exception)
#
# Decision logic:
#   INCLUDE = every inclusion criterion passes AND every exclusion criterion fails
#   EXCLUDE = any inclusion criterion fails OR any exclusion criterion passes
#
# Add more criteria to these lists as your review protocol requires.

CRITERIA = [
    {
        "id": "EC1",
        "type": "exclusion",
        "description": (
            "Non-scholarly publications (e.g., blogs, opinion pieces, "
            "white papers)."
        ),
        "clarification": "",
    },
    # ── Add more criteria below ──────────────────────────────────────────
    # {
    #     "id": "IC1",
    #     "type": "inclusion",
    #     "description": "Paper must be about agentic AI systems.",
    #     "clarification": "",
    # },
    # {
    #     "id": "EC2",
    #     "type": "exclusion",
    #     "description": "Papers not written in English.",
    #     "clarification": "",
    # },
]


# ─── 3. Prompts ──────────────────────────────────────────────────────────────

def _format_criterion_block(criterion: dict) -> str:
    block = f'Criterion [{criterion["id"]}]: "{criterion["description"]}"'
    if criterion.get("clarification"):
        block += f'\nClarification: {criterion["clarification"]}'
    return block


def build_screener_prompt(criterion: dict) -> str:
    ctype = criterion["type"]
    crit_block = _format_criterion_block(criterion)

    if ctype == "exclusion":
        decision_guidance = """\
You must decide: does this paper match the exclusion criterion?
  - If YES → the paper IS a non-scholarly publication → respond "Decision: EXCLUDE"
  - If NO  → the paper is NOT a non-scholarly publication → respond "Decision: INCLUDE"
"""
    else:
        decision_guidance = """\
You must decide: does this paper meet the inclusion criterion?
  - If YES → the paper meets the requirement → respond "Decision: INCLUDE"
  - If NO  → the paper does NOT meet the requirement → respond "Decision: EXCLUDE"
"""

    return f"""\
You are a systematic review screener. Given a paper's URL and metadata, \
evaluate it against this criterion.

{crit_block}

Steps:
1. Identify the publication source from the URL or metadata.
2. Determine whether the criterion applies to this paper.
3. Apply the criterion (and any clarification) carefully.

{decision_guidance}
If the reviewer has provided feedback on your previous decision, \
carefully reconsider and respond with a revised decision incorporating \
that feedback.

You MUST respond in EXACTLY this format (no extra text):
Decision: INCLUDE or EXCLUDE
Reason: One sentence explaining why."""


def build_reviewer_prompt(criterion: dict) -> str:
    crit_block = _format_criterion_block(criterion)

    return f"""\
You are a quality-assurance reviewer for a systematic review screening process.

{crit_block}

Review the screener's decision for a paper. Check:
1. Did the screener correctly identify the publication source?
2. Was the criterion applied correctly?
3. Was any clarification honored?
4. Is the Decision (INCLUDE/EXCLUDE) consistent with the stated Reason?

If the decision is correct, say "APPROVED" and briefly confirm why.
If there is an error, explain what is wrong and what the correct \
decision should be. Keep response under 50 words."""


# ─── 4. Agent State ──────────────────────────────────────────────────────────

class ScreenerAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


# ─── 5. ScreenerAgent Class ──────────────────────────────────────────────────

class ScreenerAgent:
    """Reflection agent that evaluates a paper against a single criterion."""

    def __init__(self, model, screener_prompt, reviewer_prompt,
                 max_iterations=2, debug=False):
        self.model = model
        self.screener_prompt = screener_prompt
        self.reviewer_prompt = reviewer_prompt
        self.max_iterations = max_iterations
        self.debug = debug

        graph = StateGraph(ScreenerAgentState)
        graph.add_node("screener", self.screen_paper)
        graph.add_node("reviewer", self.review_decision)

        graph.add_conditional_edges(
            "screener",
            self.should_continue,
            {True: "reviewer", False: END},
        )
        graph.add_edge("reviewer", "screener")
        graph.set_entry_point("screener")

        self.memory = MemorySaver()
        self.graph = graph.compile(checkpointer=self.memory)

    def screen_paper(self, state: ScreenerAgentState):
        messages = [SystemMessage(content=self.screener_prompt)] + state["messages"]
        result = self.model.invoke(messages)
        if self.debug:
            print(f"  Screener: {result.content}")
        return {"messages": [result]}

    def review_decision(self, state: ScreenerAgentState):
        messages = [SystemMessage(content=self.reviewer_prompt)] + state["messages"]
        result = self.model.invoke(messages)
        if self.debug:
            print(f"  Reviewer: {result.content}")
        return {"messages": [result]}

    def should_continue(self, state: ScreenerAgentState):
        total_iterations = len(state["messages"]) // 2
        return total_iterations < self.max_iterations


# ─── 6. Parse Decision from LLM Output ───────────────────────────────────────

def parse_criterion_result(text: str) -> tuple[str, str]:
    """Extract Decision (INCLUDE/EXCLUDE) and Reason from the screener's output."""
    decision = "UNKNOWN"
    reason = ""

    decision_match = re.search(r"Decision:\s*(INCLUDE|EXCLUDE)", text, re.IGNORECASE)
    if decision_match:
        decision = decision_match.group(1).upper()

    reason_match = re.search(r"Reason:\s*(.+)", text, re.IGNORECASE)
    if reason_match:
        reason = reason_match.group(1).strip()

    return decision, reason


# ─── 7. Aggregate Per-Criterion Results into Final Decision ──────────────────

def aggregate_decision(criterion_results: list[dict]) -> tuple[str, str]:
    """
    Apply systematic review decision logic:
      INCLUDE = every criterion says INCLUDE
      EXCLUDE = any criterion says EXCLUDE

    Each criterion's screener already outputs INCLUDE/EXCLUDE with the
    correct polarity (exclusion criteria say EXCLUDE when they match,
    inclusion criteria say EXCLUDE when not met).

    Returns (decision, reason) where reason lists the failing criteria.
    """
    exclude_reasons = []

    for cr in criterion_results:
        if cr["decision"] == "EXCLUDE":
            exclude_reasons.append(f"[{cr['id']}] {cr['reason']}")

    if exclude_reasons:
        return "EXCLUDE", "; ".join(exclude_reasons)
    else:
        return "INCLUDE", "All inclusion criteria met and no exclusion criteria triggered."


# ─── 8. Format Paper Metadata ────────────────────────────────────────────────

def format_paper_for_screening(row: pd.Series) -> str:
    """Format a paper's metadata into a screening prompt."""
    parts = [f"Paper URL: {row['URL']}"]
    if pd.notna(row.get("Title")):
        parts.append(f"Title: {row['Title']}")
    if pd.notna(row.get("DOI")) and row["DOI"]:
        parts.append(f"DOI: {row['DOI']}")
    if pd.notna(row.get("authors")):
        parts.append(f"Authors: {row['authors']}")
    if pd.notna(row.get("Abstract")):
        abstract = str(row["Abstract"])[:500]
        parts.append(f"Abstract (first 500 chars): {abstract}")
    return "\n".join(parts)


# ─── 9. Build the Screening Pipeline ─────────────────────────────────────────

def screen_papers(input_csv: Path, output_csv: Path,
                  criteria: list[dict] = CRITERIA, debug=False):
    """
    Main pipeline:
      1. Reads input CSV
      2. For each paper, evaluates every criterion via a reflection agent
      3. Aggregates per-criterion results into a final INCLUDE/EXCLUDE
      4. Writes results to output CSV
    """
    df = pd.read_csv(input_csv)
    print(f"Loaded {len(df)} papers from {input_csv.name}")
    print(f"Evaluating against {len(criteria)} criteria: "
          f"{[c['id'] for c in criteria]}")

    agents = {}
    for criterion in criteria:
        agents[criterion["id"]] = ScreenerAgent(
            model,
            build_screener_prompt(criterion),
            build_reviewer_prompt(criterion),
            max_iterations=2,
            debug=debug,
        )

    results = []

    for idx, row in df.iterrows():
        paper_id = row.get("ID", idx + 1)
        title = row.get("Title", "Unknown")
        url = row.get("URL", "")

        print(f"\n[{paper_id}/{len(df)}] Screening: {title[:60]}...")

        paper_text = format_paper_for_screening(row)
        criterion_results = []

        for criterion in criteria:
            cid = criterion["id"]
            agent = agents[cid]

            if debug:
                print(f"  Criterion {cid} ({criterion['type']}):")

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            messages = [HumanMessage(content=paper_text)]
            result = agent.graph.invoke({"messages": messages}, config)

            final_text = result["messages"][-1].content
            crit_decision, reason = parse_criterion_result(final_text)

            criterion_results.append({
                "id": cid,
                "type": criterion["type"],
                "decision": crit_decision,
                "reason": reason,
            })

        decision, decision_reason = aggregate_decision(criterion_results)

        if debug:
            print(f"  Final: {decision} — {decision_reason}")

        row_result = {
            "ID": paper_id,
            "Title": title,
            "URL": url,
            "Decision": decision,
            "Reason": decision_reason,
        }
        for cr in criterion_results:
            row_result[f"{cr['id']}_decision"] = cr["decision"]
            row_result[f"{cr['id']}_reason"] = cr["reason"]

        results.append(row_result)

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_csv, index=False, quoting=csv.QUOTE_ALL)
    print(f"\n{'=' * 60}")
    print(f"Screening complete. Results written to {output_csv.name}")
    print(f"{'=' * 60}")

    include_count = len(results_df[results_df["Decision"] == "INCLUDE"])
    exclude_count = len(results_df[results_df["Decision"] == "EXCLUDE"])
    print(f"  INCLUDE: {include_count}")
    print(f"  EXCLUDE: {exclude_count}")

    return results_df


# ─── 10. Run ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Paper Screener — Systematic Review Screening (Reflection)")
    print("=" * 60)
    screen_papers(INPUT_CSV, OUTPUT_CSV, debug=True)
