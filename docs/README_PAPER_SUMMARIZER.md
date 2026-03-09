# Paper PDF Summarizer — Design

> **Batch summarization system** that downloads academic paper PDFs, extracts text, and generates structured summaries using an LLM — producing a CSV of summaries ready for systematic review or literature mapping.

**File:** [`langgraph_examples/example13_paper_summarizer.py`](../langgraph_examples/example13_paper_summarizer.py)

---

## Overview

Reading and summarizing dozens or hundreds of papers is one of the most time-consuming tasks in a systematic review. This example automates it: for each paper in a CSV, it downloads the PDF, extracts the full text, and generates a structured summary via a LangGraph agent.

| Layer | Responsibility |
|-------|---------------|
| **PDF Downloader** | Fetches the paper PDF from the URL (with caching to `data/pdfs/`) |
| **Text Extractor** | Extracts text from the PDF using `pypdf`, capped at 20 pages |
| **Summarizer Node** | LLM node that produces a structured summary (objective, method, findings, significance) |
| **Batch Pipeline** | Reads `data/papers.csv`, processes each paper, writes `data/paper_summaries.csv` |

---

## Architecture Diagram

```
                    ┌──────────────────────────────────────────────────┐
                    │        Paper Summarizer (LangGraph)              │
                    │                                                  │
                    │  For each paper:                                 │
  papers.csv ──►   │    1. Download PDF from URL                      │  ──► paper_summaries.csv
  (100 papers)     │    2. Extract text (pypdf)                       │      (100 summaries)
                    │    3. START → Summarize → END                   │
                    │                                                  │
                    │  PDFs cached in data/pdfs/                       │
                    └──────────────────────────────────────────────────┘
```

---

## Pipeline — Step by Step

### 1. Read Input CSV

The pipeline reads `data/papers.csv` which contains columns: `ID`, `Title`, `authors`, `Abstract`, `arxiv_id`, `URL`, `DOI`.

### 2. Download PDF

For each paper, the PDF is downloaded from the `URL` column (typically an arXiv PDF link like `https://arxiv.org/pdf/2602.00359v1`). Downloaded PDFs are cached in `data/pdfs/` using the `arxiv_id` as the filename — subsequent runs skip already-downloaded files.

### 3. Extract Text

Text is extracted from the PDF using `pypdf.PdfReader`. Extraction is capped at 20 pages to keep processing manageable. The extracted text is then truncated to 12,000 characters to fit within the LLM's context budget.

### 4. Summarize (LangGraph Node)

The extracted text (with title and authors) is sent to a LangGraph agent with a single `summarize` node. The LLM produces a structured summary following a fixed format:

```
**Objective:** What the paper aims to achieve.
**Method:** The approach or methodology.
**Key Findings:** Main results.
**Significance:** Why this work matters.
```

### 5. Write Output CSV

All summaries are collected into a DataFrame and written to `data/paper_summaries.csv`.

---

## Graph Design

```
START → summarize → END
```

The graph is intentionally minimal — a single LLM node with a system prompt that enforces structured output. This keeps the pipeline fast for batch processing (one LLM call per paper instead of a reflection loop).

For higher-quality summaries, you could extend this to use the reflection pattern (like Example 10) by adding a reviewer node. The trade-off is 2-3x more LLM calls per paper.

---

## Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  Input: papers.csv                                               │
│  Columns: ID, Title, authors, Abstract, arxiv_id, URL, DOI      │
└──────────────────────────────────┬───────────────────────────────┘
                                   │ for each paper
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│  Download PDF from URL                                           │
│  Cache to data/pdfs/{arxiv_id}.pdf                               │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│  Extract text (pypdf, max 20 pages, truncate to 12K chars)       │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│  LangGraph Agent                                                 │
│  messages:                                                       │
│    [0] SystemMessage — summarizer prompt (structured format)     │
│    [1] HumanMessage  — title + authors + paper text              │
│    [2] AIMessage     — structured summary                        │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│  Output: paper_summaries.csv                                     │
│  Columns: ID, Title, URL, Summary                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Summary

| Component | Role | Implementation |
|-----------|------|----------------|
| **`download_pdf`** | Fetches PDF from URL with caching | `requests.get` with User-Agent header |
| **`extract_text_from_pdf`** | Converts PDF bytes to text | `pypdf.PdfReader`, capped at 20 pages |
| **`truncate_text`** | Keeps text within LLM context budget | Truncates at 12,000 characters |
| **`SummarizerAgent`** | LangGraph agent with single summarize node | LLM node with structured prompt |
| **`format_paper_input`** | Builds prompt from title + authors + text | Combines metadata with extracted text |
| **`summarize_papers`** | Batch pipeline orchestrator | Reads CSV → download → extract → summarize → write CSV |
| **MemorySaver** | Per-paper conversation memory | Each paper gets a unique `thread_id` |

---

## Output Format

The output CSV (`data/paper_summaries.csv`) contains:

| Column | Description |
|--------|-------------|
| `ID` | Paper ID from the input CSV |
| `Title` | Paper title |
| `URL` | Paper URL |
| `Summary` | Structured summary (Objective, Method, Key Findings, Significance) |

---

## Example Output

```csv
"ID","Title","URL","Summary"
"1","Position: Agentic Evolution is the Path to Evolving LLMs","https://arxiv.org/pdf/2602.00359v1","**Objective:** Proposes agentic evolution as a new scaling axis for LLM adaptation beyond static training.
**Method:** Introduces the A-Evolve framework, which treats deployment-time improvement as a deliberate, goal-directed optimization process over persistent system state, using an autonomous evolver agent.
**Key Findings:** Static training cannot keep pace with deployment environment changes; agentic evolution enables sustained, open-ended adaptation by allocating compute to evolution rather than just training or inference.
**Significance:** Establishes a principled framework for continuous LLM improvement in real-world deployment."
```

---

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `save_pdfs` | `True` | Cache downloaded PDFs in `data/pdfs/` |
| `max_pages` | `20` | Max PDF pages to extract text from |
| `max_chars` | `12000` | Max characters sent to the LLM |
| `delay` | `1.0` | Seconds to wait between papers (rate limiting) |
| `debug` | `True` | Print summary previews during processing |

---

## LangGraph Concepts Used

| Concept | How It Appears |
|---------|---------------|
| **LLM node** | Summarizer generates a structured summary |
| **Agent State** | Messages accumulate through the graph |
| **Batch processing** | Pipeline iterates over all papers in the CSV |
| **Structured output** | System prompt enforces Objective/Method/Findings/Significance format |
| **Per-paper memory** | Each paper gets a unique `thread_id` |

---

## Run

```bash
pip install pandas pypdf requests langchain-openai python-dotenv langgraph
python langgraph_examples/example13_paper_summarizer.py
```

**Input:** `data/papers.csv` (100 papers)
**Output:** `data/paper_summaries.csv` (100 summaries)
**Cached PDFs:** `data/pdfs/` (one PDF per paper)

The script prints progress as it downloads, extracts, and summarizes each paper.
