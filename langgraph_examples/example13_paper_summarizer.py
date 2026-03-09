# file: langgraph_examples/example13_paper_summarizer.py
"""
Paper PDF Summarizer — Download & Summarize Pipeline
─────────────────────────────────────────────────────
An agentic system that reads a CSV of academic papers, downloads each
paper's PDF, extracts the text, and produces a concise summary using
an LLM. Results are written to a CSV file.

Pipeline (per paper):
  1. Download PDF from the URL
  2. Extract text from the PDF
  3. Summarize the text via LLM (LangGraph node)

Graph design:
  START → summarize_paper → END

See also: docs/README_PAPER_SUMMARIZER.md for design doc.
"""

import csv
import io
import os
import time
import uuid
from pathlib import Path

import pandas as pd
import requests
from pypdf import PdfReader

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
OUTPUT_DIR = PROJECT_ROOT / "output"
PDF_DIR = OUTPUT_DIR / "pdfs"
INPUT_CSV = DATA_DIR / "papers.csv"
OUTPUT_CSV = OUTPUT_DIR / "paper_summaries.csv"


# ─── 1. Setup LLM ────────────────────────────────────────────────────────────
model = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.3,
)


# ─── 2. Prompts ──────────────────────────────────────────────────────────────

SUMMARIZER_PROMPT = """\
You are an expert academic paper summarizer. Given the full text of a \
research paper, produce a structured summary.

Your summary MUST follow this exact format:

**Objective:** One sentence describing what the paper aims to achieve.
**Method:** 2-3 sentences describing the approach or methodology.
**Key Findings:** 2-3 sentences highlighting the main results.
**Significance:** One sentence on why this work matters.

Keep the total summary under 150 words. Use precise, academic language. \
Do not include filler phrases like "This paper presents..." — go \
straight to the substance."""


# ─── 3. PDF Download & Text Extraction ───────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def download_pdf(url: str, save_path: Path | None = None,
                 timeout: int = 30) -> bytes | None:
    """Download a PDF from a URL. Optionally save to disk."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()

        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(resp.content)

        return resp.content
    except requests.RequestException as e:
        print(f"    [ERROR] Download failed: {e}")
        return None


def extract_text_from_pdf(pdf_bytes: bytes, max_pages: int = 20) -> str:
    """Extract text from PDF bytes, capping at max_pages."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = reader.pages[:max_pages]
        text = "\n\n".join(page.extract_text() or "" for page in pages)
        text = text.encode("utf-8", errors="replace").decode("utf-8")
        return text.strip()
    except Exception as e:
        print(f"    [ERROR] PDF extraction failed: {e}")
        return ""


def truncate_text(text: str, max_chars: int = 12000) -> str:
    """Truncate text to fit within the LLM's context budget."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... text truncated ...]"


# ─── 4. Agent State ──────────────────────────────────────────────────────────

class SummarizerState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


# ─── 5. SummarizerAgent Class ────────────────────────────────────────────────

class SummarizerAgent:
    """Simple LangGraph agent that summarizes paper text."""

    def __init__(self, model, system_prompt, debug=False):
        self.model = model
        self.system_prompt = system_prompt
        self.debug = debug

        graph = StateGraph(SummarizerState)
        graph.add_node("summarize", self.summarize)
        graph.set_entry_point("summarize")
        graph.add_edge("summarize", END)

        self.memory = MemorySaver()
        self.graph = graph.compile(checkpointer=self.memory)

    def summarize(self, state: SummarizerState):
        messages = [SystemMessage(content=self.system_prompt)] + state["messages"]
        result = self.model.invoke(messages)
        if self.debug:
            print(f"    Summary: {result.content[:120]}...")
        return {"messages": [result]}


# ─── 6. Format Paper Text for Summarization ──────────────────────────────────

def format_paper_input(title: str, authors: str, pdf_text: str) -> str:
    """Build the prompt payload sent to the LLM."""
    header = f"Title: {title}\nAuthors: {authors}\n\n"
    body = truncate_text(pdf_text)
    return header + "Full paper text:\n" + body


# ─── 7. Batch Pipeline ───────────────────────────────────────────────────────

def summarize_papers(input_csv: Path, output_csv: Path,
                     save_pdfs: bool = True, debug: bool = False,
                     delay: float = 1.0):
    """
    Main pipeline:
      1. Read input CSV
      2. For each paper: download PDF → extract text → summarize
      3. Write results to output CSV
    """
    df = pd.read_csv(input_csv)
    print(f"Loaded {len(df)} papers from {input_csv.name}")

    agent = SummarizerAgent(model, SUMMARIZER_PROMPT, debug=debug)

    results = []
    success_count = 0
    fail_count = 0

    for idx, row in df.iterrows():
        paper_id = row.get("ID", idx + 1)
        title = row.get("Title", "Unknown")
        authors = row.get("authors", "Unknown")
        url = row.get("URL", "")
        arxiv_id = row.get("arxiv_id", "")

        print(f"\n[{paper_id}/{len(df)}] {title[:65]}...")

        # ── Download PDF ──────────────────────────────────────────────
        save_path = None
        if save_pdfs and arxiv_id:
            safe_name = str(arxiv_id).replace("/", "_")
            save_path = PDF_DIR / f"{safe_name}.pdf"

        if save_path and save_path.exists():
            print(f"    PDF cached: {save_path.name}")
            pdf_bytes = save_path.read_bytes()
        else:
            print(f"    Downloading: {url}")
            pdf_bytes = download_pdf(url, save_path=save_path)

        if pdf_bytes is None:
            print(f"    SKIPPED — download failed")
            results.append({
                "ID": paper_id, "Title": title, "URL": url,
                "Summary": "[DOWNLOAD FAILED]",
            })
            fail_count += 1
            continue

        # ── Extract text ──────────────────────────────────────────────
        pdf_text = extract_text_from_pdf(pdf_bytes)
        if not pdf_text:
            print(f"    SKIPPED — no text extracted from PDF")
            results.append({
                "ID": paper_id, "Title": title, "URL": url,
                "Summary": "[TEXT EXTRACTION FAILED]",
            })
            fail_count += 1
            continue

        print(f"    Extracted {len(pdf_text):,} chars from PDF")

        # ── Summarize via LangGraph agent ─────────────────────────────
        paper_input = format_paper_input(title, authors, pdf_text)
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        messages = [HumanMessage(content=paper_input)]

        try:
            result = agent.graph.invoke({"messages": messages}, config)
            summary = result["messages"][-1].content
            success_count += 1
        except Exception as e:
            print(f"    [ERROR] LLM summarization failed: {e}")
            summary = f"[SUMMARIZATION FAILED: {e}]"
            fail_count += 1

        results.append({
            "ID": paper_id,
            "Title": title,
            "URL": url,
            "Summary": summary,
        })

        if delay > 0:
            time.sleep(delay)

    # ── Write results ─────────────────────────────────────────────────
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_csv, index=False, quoting=csv.QUOTE_ALL)

    print(f"\n{'=' * 60}")
    print(f"Summarization complete. Results written to {output_csv.name}")
    print(f"{'=' * 60}")
    print(f"  Successful: {success_count}")
    print(f"  Failed:     {fail_count}")
    print(f"  Total:      {len(results)}")

    return results_df


# ─── 8. Run ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Paper Summarizer — Download PDFs & Generate Summaries")
    print("=" * 60)
    summarize_papers(INPUT_CSV, OUTPUT_CSV, save_pdfs=True, debug=True)
