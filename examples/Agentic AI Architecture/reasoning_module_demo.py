"""
Reasoning Module Demo — Planning, Decision Logic, Problem-Solving

Uses REAL LLM calls (DeepSeek for analysis, OpenAI for reflection).
Requires: DEEPSEEK_API_KEY, OPENAI_API_KEY in .env

Run from project root:
    python examples/"Agentic AI Architecture"/reasoning_module_demo.py
"""

import os
import sys
from pathlib import Path

# Add project root (parent.parent.parent: Agentic AI Architecture -> examples -> project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from agentic_screener.config import CRITERIA, compute_decision
from agentic_screener.agents import (
    CRITERION_AGENTS,
    reflect,
    collect_and_decide,
)

# Reuse PDF loading from perception demo
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader  # type: ignore


# ─── LLM Setup ─────────────────────────────────────────────────────────────────
model_analysis = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0,
)

model_reflection = ChatOpenAI(
    model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=0,
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def _format_paper(paper: dict) -> str:
    """Format paper for criterion agents."""
    parts = [f"Title: {paper.get('Title', 'Unknown')}"]
    if paper.get("authors"):
        parts.append(f"Authors: {paper['authors']}")
    text = paper.get("text") or paper.get("Abstract", "")
    if text:
        parts.append(f"Paper content:\n{text[:12000]}")
    if paper.get("URL"):
        parts.append(f"URL: {paper['URL']}")
    return "\n\n".join(parts)


def _load_paper_from_pdf(pdf_path: Path) -> dict:
    """Perception: load paper from PDF."""
    reader = PdfReader(pdf_path)
    pages = reader.pages[:20]
    text = "\n\n".join(p.extract_text() or "" for p in pages)
    text = text.encode("utf-8", errors="replace").decode("utf-8").strip()
    if len(text) > 15000:
        text = text[:15000] + "\n\n[... truncated ...]"
    lines = text.split("\n")
    title = lines[0].strip() if lines else pdf_path.stem
    return {
        "Title": title[:200],
        "arxiv_id": pdf_path.stem,
        "filename": pdf_path.name,
        "text": text,
        "Abstract": text[:3000],
        "URL": f"https://arxiv.org/pdf/{pdf_path.stem}",
    }


def run_criterion_with_reflection(criterion_id: str, paper_text: str, max_reflections: int = 2) -> tuple[str, str]:
    """Run criterion agent + reflection loop. Returns (decision: Y/N, reason: str)."""
    agent_module = CRITERION_AGENTS.get(criterion_id)
    if not agent_module:
        return "N", f"Unknown criterion {criterion_id}"

    criterion_config = next((c for c in CRITERIA if c["id"] == criterion_id), None)
    if not criterion_config:
        return "N", f"No config for {criterion_id}"

    decision, reason = agent_module.evaluate(model_analysis, paper_text)

    for _ in range(max_reflections - 1):
        approved, feedback, suggested = reflect(
            model_reflection,
            criterion_id,
            criterion_config["description"],
            paper_text[:1000],
            decision,
            reason,
        )
        if approved:
            break
        if suggested:
            decision = suggested
            decision, reason = agent_module.evaluate(model_analysis, paper_text)

    return decision, reason


# ─── Example 1: Warehouse Robot — LLM for problem-solving ──────────────────────

def robot_problem_solve(model: ChatOpenAI, situation: str) -> str:
    """REASONING: LLM generates ad hoc solution for unexpected situation."""
    prompt = f"""A warehouse robot was delivering a box to room 303. It reached the door but the door is locked (unexpected — usually it's unlocked).

Situation: {situation}

What should the robot do? Give ONE concrete action in 1-2 sentences."""

    result = model.invoke([HumanMessage(content=prompt)])
    return result.content.strip()


def run_robot_scenario():
    """Warehouse robot: planning, predefined logic, LLM problem-solving."""
    print("=" * 65)
    print("REASONING MODULE — Warehouse Robot (Real LLM for Problem-Solving)")
    print("=" * 65)

    print("\n1. PLANNING")
    print("   Plan: Navigate to room 303 → Open door → Place box")

    print("\n2. DECISION (expected: human blocking)")
    print("   Predefined: human blocks path → detour (no LLM needed)")

    print("\n3. FEEDBACK: Attempted OPEN_DOOR → FAILED (door locked)")
    print("   Unexpected situation — invoking LLM for problem-solving...")

    print("\n4. PROBLEM-SOLVING (real LLM call)")
    situation = "Door to room 303 is locked. Robot has no key. Warehouse manager has access."
    solution = robot_problem_solve(model_analysis, situation)
    print(f"   LLM solution: {solution[:200]}...")

    print("\n5. PERCEPTION REFINEMENT")
    print("   Reasoning → Perception: 'Tag door keypad light (locked/unlocked)'")
    print("   Next time: Check before attempting; if locked, text manager immediately")
    print("=" * 65)


# ─── Example 2: Paper Screening Agent — Real criterion agents + reflection ──────

def run_paper_screening_demo():
    """Paper screening: real LLM calls for criteria, reflection, and decision."""
    print("\n" + "=" * 65)
    print("REASONING MODULE — Paper Screening Agent (Real LLM Calls)")
    print("=" * 65)

    pdf_dir = _PROJECT_ROOT / "output" / "pdfs"
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDFs in output/pdfs/. Add some PDFs first.")
        return

    # Perception: load one paper
    paper = _load_paper_from_pdf(pdf_files[0])
    paper_text = _format_paper(paper)

    print(f"\n1. PERCEPTIONS (from Perception Module)")
    print(f"   Title: {paper['Title'][:60]}...")
    print(f"   Arxiv: {paper['arxiv_id']}")

    print("\n2. PLANNING")
    plan = list(CRITERION_AGENTS.keys())
    print(f"   Plan: Evaluate criteria in order: {plan}")

    print("\n3. MODEL LOGIC (real LLM calls — DeepSeek for each criterion)")
    criterion_results = {}
    for cid in plan:
        dec, reason = run_criterion_with_reflection(cid, paper_text)
        criterion_results[cid] = (dec, reason)
        print(f"   [{cid}] {dec}: {reason[:60]}...")

    print("\n4. REFLECTION (real LLM call — GPT-4o-mini validates each criterion)")
    print("   (Reflection runs inside run_criterion_with_reflection)")

    print("\n5. DECISION RULE (predefined logic)")
    include, reason = collect_and_decide(criterion_results)[:2]
    print(f"   Decision: {'INCLUDE' if include else 'EXCLUDE'}")
    print(f"   Reason: {reason}")

    print("\n6. INFERENCE ENGINE")
    print("   LangChain + agentic_screener orchestrates model calls, applies rules")
    print("=" * 65)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("Error: DEEPSEEK_API_KEY not set. Add to .env")
        sys.exit(1)
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set. Add to .env")
        sys.exit(1)

    run_robot_scenario()
    run_paper_screening_demo()


if __name__ == "__main__":
    main()
