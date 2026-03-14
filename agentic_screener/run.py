"""
Agentic Paper Screener — Main Orchestration
──────────────────────────────────────────
Multi-agent system that screens papers in parallel.
Input: PDF files from output/pdfs/ (or INPUT_PDF_DIR). Fallback: CSV.

Run: python -m agentic_screener.run
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader  # type: ignore

from langchain_openai import ChatOpenAI

from agentic_screener.config import (
    CRITERIA,
    INPUT_CSV,
    INPUT_PDF_DIR,
    OUTPUT_CSV,
    OUTPUT_SUMMARIES_CSV,
)
from agentic_screener.agents import (
    CRITERION_AGENTS,
    reflect,
    collect_and_decide,
    generate_csv,
    get_default_columns,
    summarize_paper,
)

load_dotenv()

# ─── LLM Setup ─────────────────────────────────────────────────────────────────
# Analysis (criterion agents, summary): DeepSeek
# Reflection: OpenAI

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


# ─── PDF extraction ────────────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_path: Path, max_pages: int = 20, max_chars: int = 15000) -> str:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        pages = reader.pages[:max_pages]
        text = "\n\n".join(page.extract_text() or "" for page in pages)
        text = text.encode("utf-8", errors="replace").decode("utf-8")
        text = text.strip()
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[... text truncated ...]"
        return text
    except Exception as e:
        return f"[PDF extraction failed: {e}]"


def load_papers_from_pdfs(pdf_dir: Path, limit: int | None = None) -> list[dict]:
    """Load papers from PDF directory."""
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if limit:
        pdf_files = pdf_files[:limit]
    papers = []
    for i, pdf_path in enumerate(pdf_files):
        text = extract_text_from_pdf(pdf_path)
        first_lines = text.split("\n")[:5]
        title = first_lines[0].strip() if first_lines else pdf_path.stem
        if len(title) > 200:
            title = title[:200] + "..."
        papers.append({
            "ID": i + 1,
            "filename": pdf_path.name,
            "arxiv_id": pdf_path.stem,
            "Title": title,
            "authors": "",
            "Abstract": text[:3000] if len(text) > 3000 else text,
            "text": text,
            "URL": f"https://arxiv.org/pdf/{pdf_path.stem}",
        })
    return papers


# ─── Format paper for screening ────────────────────────────────────────────────
def format_paper(paper: dict | pd.Series) -> str:
    """Format paper for criterion agents. Accepts dict (from PDF) or pd.Series (from CSV)."""
    if isinstance(paper, dict):
        parts = [f"Title: {paper.get('Title', 'Unknown')}"]
        if paper.get("authors"):
            parts.append(f"Authors: {paper['authors']}")
        text = paper.get("text") or paper.get("Abstract", "")
        if text:
            parts.append(f"Paper content:\n{text[:12000]}")
        if paper.get("URL"):
            parts.append(f"URL: {paper['URL']}")
        return "\n\n".join(parts)
    parts = [f"Title: {paper.get('Title', 'Unknown')}"]
    if pd.notna(paper.get("authors")):
        parts.append(f"Authors: {paper['authors']}")
    if pd.notna(paper.get("Abstract")) and str(paper["Abstract"]).strip():
        parts.append(f"Abstract: {str(paper['Abstract'])[:2000]}")
    if pd.notna(paper.get("URL")):
        parts.append(f"URL: {paper['URL']}")
    return "\n\n".join(parts)


# ─── Run one criterion with reflection ─────────────────────────────────────────
def run_criterion_with_reflection(criterion_id: str, paper_text: str, max_reflections: int = 2) -> tuple[str, str]:
    """
    Run criterion agent + reflection loop. Returns (decision: Y/N, reason: str).
    """
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
            # Re-run criterion with reflection feedback (simplified: use suggested)
            decision, reason = agent_module.evaluate(model_analysis, paper_text)

    return decision, reason


# ─── Process one paper (all criteria in parallel) ──────────────────────────────
def process_paper(paper: dict | pd.Series, paper_id: int, total: int, debug: bool = False) -> dict:
    """Process a single paper: run all criteria in parallel, collect, decide, summarize if included."""
    paper_text = format_paper(paper)
    criterion_ids = list(CRITERION_AGENTS.keys())

    # Run criterion agents in parallel
    criterion_results = {}
    with ThreadPoolExecutor(max_workers=len(criterion_ids)) as executor:
        future_to_cid = {
            executor.submit(run_criterion_with_reflection, cid, paper_text): cid
            for cid in criterion_ids
        }
        for future in as_completed(future_to_cid):
            cid = future_to_cid[future]
            try:
                dec, reason = future.result()
                criterion_results[cid] = (dec, reason)
                if debug:
                    print(f"    [{cid}] {dec}: {reason[:50]}...")
            except Exception as e:
                criterion_results[cid] = ("N", str(e))
                if debug:
                    print(f"    [{cid}] ERROR: {e}")

    # Collector: aggregate and decide
    include, decision_reason = collect_and_decide(criterion_results)[:2]
    decision = "Yes" if include else "No"

    # Build result row (paper can be dict from PDF or pd.Series from CSV)
    def get_val(key: str, default=""):
        v = paper.get(key, default) if isinstance(paper, dict) else paper.get(key, default)
        if v is None or (isinstance(v, float) and pd.isna(v)):
            v = default
        return str(v)[:500] if key == "Abstract" else (str(v) if v else default)

    result = {
        "ID": get_val("ID", paper_id),
        "Title": get_val("Title", "Unknown"),
        "authors": get_val("authors", ""),
        "Abstract": get_val("Abstract", "")[:500],
        "arxiv_id": get_val("arxiv_id", ""),
        "URL": get_val("URL", ""),
        "DOI": get_val("DOI", ""),
        "filename": get_val("filename", "") if isinstance(paper, dict) else "",
        "Decision": decision,
        "Reason": decision_reason,
    }
    for cid in criterion_ids:
        dec, reason = criterion_results[cid]
        result[cid] = dec
        result[f"{cid}_reason"] = reason

    # Summary agent: only for included papers (uses analysis model)
    if include:
        try:
            title = get_val("Title", "")
            authors = get_val("authors", "")
            abstract = get_val("Abstract", "") or (paper.get("text", "")[:2000] if isinstance(paper, dict) else "")
            summary = summarize_paper(model_analysis, title, authors, abstract)
            result["Summary"] = summary
        except Exception as e:
            result["Summary"] = f"[Summary failed: {e}]"
    else:
        result["Summary"] = ""

    return result


# ─── Main pipeline ─────────────────────────────────────────────────────────────
def run_screening(
    input_pdf_dir: Path | None = None,
    input_csv: Path | None = None,
    output_csv: Path = OUTPUT_CSV,
    output_summaries_csv: Path | None = None,
    limit: int | None = None,
    debug: bool = True,
):
    """
    Main pipeline. Input: PDF files from input_pdf_dir (default: output/pdfs).
    Fallback: CSV from input_csv if PDF dir is empty or missing.
    """
    input_pdf_dir = input_pdf_dir or INPUT_PDF_DIR
    papers: list = []

    if input_pdf_dir.exists():
        papers = load_papers_from_pdfs(input_pdf_dir, limit=limit)
        print(f"Loaded {len(papers)} papers from PDFs in {input_pdf_dir.name}")
    else:
        print(f"PDF directory not found: {input_pdf_dir}")

    if not papers and (input_csv or INPUT_CSV).exists():
        csv_path = input_csv or INPUT_CSV
        try:
            df = pd.read_csv(csv_path, header=1)
        except Exception:
            df = pd.read_csv(csv_path)
        if limit:
            df = df.head(limit)
        papers = [row for _, row in df.iterrows()]
        print(f"Loaded {len(papers)} papers from CSV {csv_path.name}")

    if not papers:
        print("No papers to process. Add PDFs to output/pdfs/ or provide a CSV.")
        return

    total = len(papers)
    print(f"Criteria: {list(CRITERION_AGENTS.keys())}")
    print(f"Models: DeepSeek (analysis), OpenAI (reflection)")
    print("=" * 60)

    results = []
    for idx, paper in enumerate(papers):
        paper_id = paper.get("ID", idx + 1) if isinstance(paper, dict) else paper.get("ID", idx + 1)
        title = paper.get("Title", "Unknown") if isinstance(paper, dict) else paper.get("Title", "Unknown")
        print(f"\n[{paper_id}/{total}] {str(title)[:65]}...")
        result = process_paper(paper, paper_id, total, debug=debug)
        results.append(result)
        if debug:
            print(f"  Final: {result['Decision']} — {result['Reason'][:60]}...")

    # CSV generator agent
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    generate_csv(results, output_csv, columns=get_default_columns())
    print(f"\n{'=' * 60}")
    print(f"Results written to {output_csv}")

    # Optional: summaries CSV for included papers only
    if output_summaries_csv:
        included = [r for r in results if r["Decision"] == "Yes"]
        if included:
            summaries_df = pd.DataFrame(
                [
                    {
                        "ID": r["ID"],
                        "Title": r["Title"],
                        "Summary": r.get("Summary", ""),
                    }
                    for r in included
                ]
            )
            summaries_df.to_csv(output_summaries_csv, index=False, quoting=1)
            print(f"Included summaries written to {output_summaries_csv}")

    include_count = sum(1 for r in results if r["Decision"] == "Yes")
    exclude_count = total - include_count
    print(f"  INCLUDE: {include_count}")
    print(f"  EXCLUDE: {exclude_count}")
    print("=" * 60)

    return results


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agentic Paper Screener")
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=None,
        help="Number of files to process (default: all)",
    )
    parser.add_argument(
        "--no-debug",
        action="store_true",
        help="Disable debug output",
    )
    args = parser.parse_args()
    limit = args.limit
    if limit is None and os.environ.get("LIMIT"):
        limit = int(os.environ["LIMIT"])

    print("=" * 60)
    print("Agentic Paper Screener — Multi-Agent Parallel Screening")
    print("=" * 60)
    run_screening(
        input_pdf_dir=INPUT_PDF_DIR,
        limit=limit,
        debug=not args.no_debug,
        output_summaries_csv=OUTPUT_SUMMARIES_CSV,
    )
