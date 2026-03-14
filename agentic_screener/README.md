# Agentic Paper Screener

Multi-agent system for screening academic papers against inclusion/exclusion criteria. Each agent runs in parallel, with reflection for quality assurance.

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │     Paper Input (PDFs or CSV)             │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │     PARALLEL CRITERION AGENTS             │
                    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ...   │
                    │  │ I1  │ │ I2  │ │ E1  │ │ E2  │         │
                    │  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘         │
                    │     │       │       │       │            │
                    │     ▼       ▼       ▼       ▼            │
                    │  REFLECTION (per criterion)              │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │         COLLECTOR AGENT                   │
                    │  Aggregates results, makes decision      │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │    SUMMARY AGENT (included papers only)   │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │        CSV GENERATOR AGENT               │
                    │  Writes screening_results.csv            │
                    └─────────────────────────────────────────┘
```

## Agents (one per file)

| File | Agent | Role |
|------|-------|------|
| `criterion_i1.py` | I1 | LLM-based agentic systems |
| `criterion_i2.py` | I2 | Energy relevance (direct or proxy) |
| `criterion_e1.py` | E1 | Not LLM-based (exclusion) |
| `criterion_e2.py` | E2 | Not agentic (exclusion) |
| `criterion_e3.py` | E3 | Energy unrelated to compute (exclusion) |
| `criterion_e7.py` | E7 | Energy as application domain only (exclusion) |
| `reflection_agent.py` | Reflection | Validates each criterion's output |
| `collector_agent.py` | Collector | Aggregates and decides INCLUDE/EXCLUDE |
| `summary_agent.py` | Summary | Summarizes included papers |
| `csv_generator_agent.py` | CSV | Writes results to CSV |

## Decision Logic

- **INCLUDE**: I1=Y AND I2=Y AND E1=N AND E2=N AND E3=N AND E7=N
- **EXCLUDE**: Otherwise

## Usage

```bash
# From project root — process all papers
python -m agentic_screener.run

# Process only 5 papers
python -m agentic_screener.run -n 5

# Or use env: LIMIT=10 python -m agentic_screener.run
```

## Input / Output

- **Input**: PDF files from `output/pdfs/` (primary). Fallback: `output/manual_review.csv`. Set `INPUT_PDF_DIR` in `.env` to override.
- **Output**: `output/agentic_screening_results.csv`
- **Summaries**: `output/agentic_included_summaries.csv` (included papers only)

## Environment

Requires both in `.env`:
- `DEEPSEEK_API_KEY` — for analysis (criterion agents, summary)
- `OPENAI_API_KEY` — for reflection (validating criterion outputs)
