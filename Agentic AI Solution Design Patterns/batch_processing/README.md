# Batch Processing Architecture

Demonstrates **Batch Processing Architecture for Agentic AI** in a data analytics platform using the Anthropic Claude API.

## 5 Use Cases

1. **Asynchronous bulk message exchange** — Data collector submits 50 records in one bulk operation
2. **Coordinated state synchronization** — 8 state updates synced in 1 batch (vs 8 individual)
3. **Workload delegation** — Data collector delegates analysis to specialized agent
4. **Cross-agent data transformation pipeline** — raw → clean → analyze → report (3 stages)
5. **Intra-agent batch queue** — 3 microservice steps (perception, reasoning, action) learned as one batch

## Architecture

- **BatchQueue** — Consumer sets minimum batch size; queue waits until threshold met
- **5 agents** — data_collector, cleansing, analysis, report, sync
- **Intra-agent** — Learning microservice processes batch when 3 tasks from one cycle

## Setup

```bash
pip install -r requirements.txt
```

Set `ANTHROPIC_API_KEY` in `.env`.

## Run

```bash
python main.py
```

## Project Structure

```
batch_processing/
├── config.py
├── batch_queue/batch_queue.py
├── agents/
│   ├── data_collector_agent.py
│   ├── cleansing_agent.py
│   ├── analysis_agent.py
│   ├── report_agent.py
│   └── sync_agent.py
├── intra_agent/learning_pipeline.py
├── scenarios/
├── prompts.py
├── llm_client.py
└── main.py
```
