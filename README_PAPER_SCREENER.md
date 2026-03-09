# Systematic Review Paper Screener — Design

> **Agentic screening system** that uses the **reflection pattern** to screen academic papers against multiple inclusion and exclusion criteria for a systematic review, outputting INCLUDE/EXCLUDE decisions with per-criterion reasoning.

**File:** [`langgraph_examples/example12_paper_screener.py`](langgraph_examples/example12_paper_screener.py)

---

## Overview

Systematic reviews require screening hundreds or thousands of papers against predefined criteria. This example automates that process using the reflection pattern: for **each** criterion, a **screener** makes an initial evaluation, a **reviewer** checks it, and the screener revises if needed. The per-criterion results are then **aggregated** into a final decision using standard systematic review logic.

| Layer | Responsibility |
|-------|---------------|
| **Screener Node** | Evaluates a paper against a single criterion → PASS/FAIL with reasoning |
| **Reviewer Node** | Quality-checks the screener's evaluation — verifies source identification and criterion application |
| **Conditional Edge** | `should_continue` — caps the reflection loop at N iterations |
| **Aggregation** | Combines per-criterion results into a final INCLUDE/EXCLUDE decision |
| **Batch Pipeline** | Reads `data/papers.csv`, invokes the agent for each paper × each criterion, writes results to `data/screening_results.csv` |

---

## Decision Logic

The final decision for each paper follows standard systematic review protocol:

```
INCLUDE = ALL inclusion criteria PASS  AND  ALL exclusion criteria FAIL
EXCLUDE = ANY inclusion criterion FAILs  OR  ANY exclusion criterion PASSes
```

| Scenario | Result |
|----------|--------|
| All inclusion criteria met, no exclusion criteria triggered | **INCLUDE** |
| One or more inclusion criteria not met | **EXCLUDE** (lists which criteria failed) |
| One or more exclusion criteria triggered | **EXCLUDE** (lists which criteria triggered) |
| Both an inclusion fails and an exclusion triggers | **EXCLUDE** (lists all failing criteria) |

---

## Criteria

Criteria are defined as a list of dictionaries, each with an `id`, `type` (inclusion/exclusion), `description`, and optional `clarification`. This makes the system extensible — add new criteria to the list as your review protocol requires.

### Current Criteria

| ID | Type | Description | Clarification |
|----|------|-------------|---------------|
| EC1 | Exclusion | Non-scholarly publications (e.g., blogs, opinion pieces, white papers) — excluding recognized preprint repositories (e.g., arXiv) | arXiv papers should NOT be excluded |

### Per-Criterion Evaluation

For each criterion, the screener outputs:
```
Result: PASS or FAIL
Reason: One sentence explaining why.
```

- **Exclusion criterion:** PASS = the criterion applies (paper should be excluded); FAIL = criterion does not apply
- **Inclusion criterion:** PASS = paper meets the requirement; FAIL = paper does not meet it

---

## Why Reflection for Screening?

A single LLM call can misapply criteria, especially with nuanced clarifications. The reflection pattern catches common mistakes:

| Mistake | How the Reviewer Catches It |
|---------|----------------------------|
| Excluding an arXiv paper | Reviewer checks the clarification and flags the error |
| Misidentifying the source | Reviewer verifies the URL domain against known repositories |
| Inconsistent reasoning | Reviewer checks if the Result matches the stated Reason |
| Over-aggressive exclusion | Reviewer confirms the source is genuinely non-scholarly |

After the reviewer's feedback, the screener revises its evaluation, producing a more reliable per-criterion result.

---

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────┐
                    │         Paper Screener (LangGraph)              │
                    │                                                 │
                    │  For each paper × each criterion:               │
  papers.csv ──►   │  START → Screener → [should_continue?]          │  ──► screening_results.csv
  (99 papers)      │                      │ yes    │ no              │      (99 decisions)
                    │                      ▼        ▼                │
                    │                   Reviewer   END               │
                    │                      │                          │
                    │                      └──► Screener (loop)      │
                    │                                                 │
                    │  Then: aggregate per-criterion results           │
                    │  → Final INCLUDE/EXCLUDE                        │
                    └─────────────────────────────────────────────────┘
```

For each paper in the input CSV:
1. Paper metadata is formatted as a `HumanMessage`
2. For **each criterion**, the reflection agent runs (screener → reviewer → screener)
3. The per-criterion Result (PASS/FAIL) is parsed from the last message
4. All per-criterion results are aggregated into a final decision
5. Results are accumulated and written to the output CSV

---

## Graph Design — Step by Step

### 1. START → Screener

The **Screener** node receives the paper's URL, title, authors, and abstract. It evaluates **one criterion** and responds with:
```
Result: PASS or FAIL
Reason: One sentence explaining why.
```

### 2. Conditional Edge — should_continue?

Checks the iteration count. If fewer than N iterations are done, routes to the **Reviewer**. Otherwise, the evaluation is final — routes to **END**.

### 3. Reviewer

The **Reviewer** examines the screener's evaluation against the specific criterion and any clarification. It checks:
- Was the relevant metadata correctly identified?
- Was the criterion applied correctly?
- Was any clarification honored?

If correct, the reviewer says "APPROVED". If wrong, it explains the error.

### 4. Loop Back → Screener (Revised)

If the reviewer found an issue, the screener sees the feedback and produces a corrected evaluation. After the maximum iterations, the final screener output is used.

### 5. Aggregation

After all criteria are evaluated for a paper, the `aggregate_decision` function applies the decision logic: **INCLUDE** only if all inclusion criteria pass and no exclusion criteria trigger.

---

## Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  Input: papers.csv                                               │
│  Columns: ID, Title, authors, Abstract, arxiv_id, URL, DOI      │
└──────────────────────────────────┬───────────────────────────────┘
                                   │ for each paper
                                   ▼
             ┌─────────────────────────────────────┐
             │  For each criterion (EC1, IC1, ...)  │
             │                                     │
             │  Agent State (per paper × criterion) │
             │  messages:                           │
             │    [0] HumanMessage — metadata       │
             │    [1] AIMessage  — "Result: ..."    │
             │    [2] AIMessage  — "APPROVED"/error  │
             │    [3] AIMessage  — final result      │
             └──────────────────┬──────────────────┘
                                │ parse per-criterion result
                                ▼
             ┌─────────────────────────────────────┐
             │  Aggregate:                          │
             │  All inclusion PASS + no exclusion   │
             │  PASS → INCLUDE                      │
             │  Otherwise → EXCLUDE (with reasons)  │
             └──────────────────┬──────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  Output: screening_results.csv                                   │
│  Columns: ID, Title, URL, Decision, Reason,                     │
│           EC1_result, EC1_reason, ...                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Summary

| Component | Role | Implementation |
|-----------|------|----------------|
| **Screener node** | Evaluates one criterion against a paper | LLM node with criterion-specific system prompt |
| **Reviewer node** | Quality-checks the evaluation | LLM node with criterion-specific reviewer prompt |
| **Conditional edge** | Caps reflection iterations | `should_continue` — checks iteration count |
| **`parse_criterion_result`** | Extracts Result + Reason from LLM text | Regex parsing of structured output |
| **`aggregate_decision`** | Combines per-criterion results into final decision | Applies inclusion/exclusion logic |
| **`build_screener_prompt`** | Generates criterion-specific screener prompt | Formats criterion type, description, clarification |
| **`build_reviewer_prompt`** | Generates criterion-specific reviewer prompt | Formats criterion for QA review |
| **`format_paper_for_screening`** | Formats CSV row into screening prompt | Builds text from URL, title, authors, abstract |
| **`screen_papers`** | Batch pipeline orchestrator | Reads CSV → invokes agent per paper × criterion → writes CSV |
| **MemorySaver** | Per-paper-per-criterion conversation memory | Each evaluation gets a unique `thread_id` |

---

## Output Format

The output CSV (`data/screening_results.csv`) contains:

| Column | Description |
|--------|-------------|
| `ID` | Paper ID from the input CSV |
| `Title` | Paper title |
| `URL` | Paper URL |
| `Decision` | `INCLUDE` or `EXCLUDE` (aggregated) |
| `Reason` | Aggregated reason (lists which criteria failed, if any) |
| `EC1_result` | Per-criterion result: `PASS` or `FAIL` |
| `EC1_reason` | Per-criterion reason |
| *(additional columns for each criterion)* | |

---

## Example Output

```csv
"ID","Title","URL","Decision","Reason","EC1_result","EC1_reason"
"1","Position: Agentic Evolution...","https://arxiv.org/pdf/2602.00359v1","INCLUDE","All inclusion criteria met and no exclusion criteria triggered.","FAIL","The paper is on arXiv, a recognized preprint repository excluded from this criterion."
```

In this example, **EC1** (exclusion criterion) gets `FAIL` — meaning the exclusion does **not** apply — so the paper is **INCLUDE**d.

---

## Adding More Criteria

To add a new criterion, append it to the `CRITERIA` list in `example12_paper_screener.py`:

```python
CRITERIA = [
    {
        "id": "EC1",
        "type": "exclusion",
        "description": "Non-scholarly publications ...",
        "clarification": "arXiv papers should NOT be excluded.",
    },
    {
        "id": "IC1",
        "type": "inclusion",
        "description": "Paper must be about agentic AI systems.",
        "clarification": "",
    },
    {
        "id": "EC2",
        "type": "exclusion",
        "description": "Papers not written in English.",
        "clarification": "",
    },
]
```

Each criterion gets its own reflection agent with tailored prompts. The aggregation logic automatically handles the new criteria.

---

## LangGraph Concepts Used

| Concept | How It Appears |
|---------|---------------|
| **Reflection pattern** | Screener evaluates, reviewer checks, screener revises |
| **LLM node (screener)** | Per-criterion evaluation with structured output |
| **LLM node (reviewer)** | Quality-assurance check on each evaluation |
| **Conditional edge** | `should_continue` caps reflection iterations |
| **Agent State** | Messages accumulate through each reflection loop |
| **Multi-criterion evaluation** | Separate reflection loop per criterion, then aggregation |
| **Batch processing** | Pipeline iterates over all papers × all criteria |
| **Structured output parsing** | Regex extracts Result/Reason from LLM text |

---

## Run

```bash
pip install pandas langchain-openai python-dotenv langgraph
python langgraph_examples/example12_paper_screener.py
```

**Input:** `data/papers.csv` (99 papers)
**Output:** `data/screening_results.csv` (99 decisions with per-criterion details)

The script prints progress as it screens each paper and a final summary with INCLUDE/EXCLUDE counts.
