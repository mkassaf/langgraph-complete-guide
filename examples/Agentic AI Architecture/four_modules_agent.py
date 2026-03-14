"""
Four-Module Agent — Perception, Reasoning, Action, Learning

A complete agent that demonstrates all four core modules working together:
1. PERCEPTION: Collect raw data → process → form perceptions
2. REASONING: Plan → decide (rules + optional LLM) → output decision
3. ACTION: Translate decision → execute via effectors → monitor
4. LEARNING: Store feedback → analyze → refine rules for next time

Run from project root:
    python examples/"Agentic AI Architecture"/four_modules_agent.py

Uses simulated reasoning (no API keys required). Set USE_REAL_LLM=1 for real LLM calls.
"""

import csv
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader  # type: ignore


# ─── PERCEPTION MODULE ───────────────────────────────────────────────────────

def perception_module(pdf_path: Path, max_chars: int = 15000) -> dict:
    """
    Perception: Collect percepts → Process → Interpret → Perceptions
    """
    # 1. Collect percepts
    raw_bytes = pdf_path.read_bytes()
    reader = PdfReader(pdf_path)
    raw_text = "\n\n".join(p.extract_text() or "" for p in reader.pages[:20])
    metadata = {"filename": pdf_path.name, "arxiv_id": pdf_path.stem}

    # 2. Process
    cleaned = raw_text.encode("utf-8", errors="replace").decode("utf-8").strip()
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "\n\n[... truncated ...]"

    # 3. Interpret → Perceptions
    lines = cleaned.split("\n")
    title = lines[0].strip() if lines else metadata["filename"]
    if len(title) > 200:
        title = title[:200] + "..."

    return {
        "title": title,
        "abstract": cleaned[:3000],
        "full_text": cleaned,
        "metadata": metadata,
    }


# ─── REASONING MODULE ────────────────────────────────────────────────────────

@dataclass
class ReasoningDecision:
    """Output of reasoning module."""
    include: bool
    reason: str
    criterion_results: dict = field(default_factory=dict)


def reasoning_module_simulated(perceptions: dict) -> ReasoningDecision:
    """
    Reasoning: Simulated (keyword-based) — no LLM.
    Uses simple heuristics for demo.
    """
    text = (perceptions.get("title", "") + " " + perceptions.get("abstract", "")).lower()

    # Simple heuristic: agent + (cost OR efficiency OR latency)
    has_agent = any(kw in text for kw in ["agent", "agentic", "multi-agent"])
    has_efficiency = any(kw in text for kw in ["cost", "efficiency", "latency", "token", "compute", "optimization"])

    if has_agent and has_efficiency:
        return ReasoningDecision(
            include=True,
            reason="Agent + efficiency keywords detected",
            criterion_results={"I1": "Y", "I2": "Y", "E1": "N", "E2": "N"},
        )
    return ReasoningDecision(
        include=False,
        reason="Missing agent or efficiency keywords",
        criterion_results={"I1": "Y" if has_agent else "N", "I2": "Y" if has_efficiency else "N"},
    )


def reasoning_module_llm(perceptions: dict) -> ReasoningDecision:
    """
    Reasoning: Real LLM (DeepSeek + reflection) — requires API keys.
    """
    from dotenv import load_dotenv
    load_dotenv()
    if not os.environ.get("DEEPSEEK_API_KEY"):
        return reasoning_module_simulated(perceptions)

    from langchain_openai import ChatOpenAI
    from agentic_screener.config import CRITERIA, compute_decision
    from agentic_screener.agents import CRITERION_AGENTS, reflect, collect_and_decide

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

    paper_text = f"Title: {perceptions['title']}\n\nPaper content:\n{perceptions['full_text'][:12000]}"

    def run_criterion(cid: str) -> tuple[str, str]:
        agent = CRITERION_AGENTS.get(cid)
        if not agent:
            return "N", "Unknown"
        dec, reason = agent.evaluate(model_analysis, paper_text)
        cfg = next((c for c in CRITERIA if c["id"] == cid), None)
        if cfg:
            approved, _, suggested = reflect(model_reflection, cid, cfg["description"], paper_text[:1000], dec, reason)
            if not approved and suggested:
                dec = suggested
        return dec, reason

    criterion_results = {cid: (run_criterion(cid)[0], "") for cid in CRITERION_AGENTS}
    include, reason = collect_and_decide(criterion_results)[:2]
    results_dict = {cid: dec for cid, (dec, _) in criterion_results.items()}

    return ReasoningDecision(include=include, reason=reason, criterion_results=results_dict)


# ─── ACTION MODULE ───────────────────────────────────────────────────────────

@dataclass
class ActionDecision:
    action_type: str
    payload: dict


def action_module(decision: ReasoningDecision, perceptions: dict) -> dict:
    """
    Action: Translate decision → Execute via effectors → Monitor
    """
    output_dir = _PROJECT_ROOT / "output" / "examples"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "four_modules_results.csv"

    payload = {
        "arxiv_id": perceptions["metadata"]["arxiv_id"],
        "title": perceptions["title"][:80],
        "decision": "Include" if decision.include else "Exclude",
        "reason": decision.reason[:100],
    }

    start = time.perf_counter()
    try:
        write_header = not csv_path.exists() or csv_path.stat().st_size == 0
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=payload.keys(), quoting=csv.QUOTE_MINIMAL)
            if write_header:
                writer.writeheader()
            writer.writerow(payload)
        success = True
        message = "Write complete"
    except Exception as e:
        success = False
        message = str(e)
    latency_ms = (time.perf_counter() - start) * 1000

    return {
        "success": success,
        "message": message,
        "latency_ms": latency_ms,
        "path": str(csv_path),
    }


# ─── LEARNING MODULE ─────────────────────────────────────────────────────────

class LearningModule:
    """Learning: Store feedback, analyze, refine rules."""

    def __init__(self):
        self.experience_log: list[dict] = []
        self.learned_rules: dict = {}

    def store_outcome(self, perceptions: dict, decision: ReasoningDecision, action_result: dict):
        """Store this run for feedback analysis."""
        self.experience_log.append({
            "arxiv_id": perceptions["metadata"]["arxiv_id"],
            "title": perceptions["title"],
            "decision": decision.include,
            "reason": decision.reason,
            "action_success": action_result["success"],
        })

    def store_manual_feedback(self, arxiv_id: str, manual_decision: bool, note: str):
        """Store manual review feedback (e.g., human correction)."""
        self.experience_log.append({
            "arxiv_id": arxiv_id,
            "feedback_type": "manual",
            "manual_decision": manual_decision,
            "note": note,
        })

    def analyze(self) -> dict:
        """Analyze experience to identify patterns."""
        manual_feedbacks = [e for e in self.experience_log if e.get("feedback_type") == "manual"]
        outcomes = [e for e in self.experience_log if e.get("feedback_type") != "manual"]

        if not manual_feedbacks and not outcomes:
            return {"pattern": "No data yet", "suggestion": "Continue collecting"}

        # Simple: if we have manual feedback, suggest refinements
        if manual_feedbacks:
            return {
                "pattern": f"{len(manual_feedbacks)} manual corrections received",
                "suggestion": "Refine E2 (agentic at inference time), E3 (agent vs target efficiency)",
            }
        return {
            "pattern": f"{len(outcomes)} papers processed",
            "suggestion": "Rules unchanged; add manual feedback to trigger learning",
        }


# ─── FULL AGENT: Four Modules Together ───────────────────────────────────────

def run_agent(pdf_path: Path, use_llm: bool = False) -> dict:
    """
    Run the full agent pipeline: Perception → Reasoning → Action → Learning
    """
    use_llm = use_llm or os.environ.get("USE_REAL_LLM") == "1"

    print("=" * 65)
    print("FOUR-MODULE AGENT — Full Pipeline")
    print("=" * 65)

    # 1. PERCEPTION
    print("\n1. PERCEPTION MODULE")
    perceptions = perception_module(pdf_path)
    print(f"   Title: {perceptions['title'][:55]}...")
    print(f"   Arxiv: {perceptions['metadata']['arxiv_id']}")

    # 2. REASONING
    print("\n2. REASONING MODULE")
    if use_llm:
        print("   Using real LLM (DeepSeek + reflection)...")
        decision = reasoning_module_llm(perceptions)
    else:
        print("   Using simulated (keyword-based) reasoning...")
        decision = reasoning_module_simulated(perceptions)
    print(f"   Decision: {'INCLUDE' if decision.include else 'EXCLUDE'}")
    print(f"   Reason: {decision.reason[:60]}...")

    # 3. ACTION
    print("\n3. ACTION MODULE")
    action_result = action_module(decision, perceptions)
    print(f"   Effector: file_system (CSV)")
    print(f"   Result: {action_result['message']} ({action_result['latency_ms']:.1f}ms)")

    # 4. LEARNING
    print("\n4. LEARNING MODULE")
    learning = LearningModule()
    learning.store_outcome(perceptions, decision, action_result)
    analysis = learning.analyze()
    print(f"   Stored outcome for {perceptions['metadata']['arxiv_id']}")
    print(f"   Analysis: {analysis['pattern']}")

    print("\n" + "=" * 65)
    return {
        "perceptions": perceptions,
        "decision": decision,
        "action_result": action_result,
        "learning_analysis": analysis,
    }


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pdf_dir = _PROJECT_ROOT / "output" / "pdfs"
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDFs in output/pdfs/. Add some PDFs first.")
        sys.exit(1)

    # Run on first PDF
    run_agent(pdf_files[0])
