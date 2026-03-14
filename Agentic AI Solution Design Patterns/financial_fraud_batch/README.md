# Financial Fraud & Risk — Batch Processing Example

A large financial company uses an agentic AI system to monitor transactions, identify potential fraud, and assess risk. Batch processing enables efficient analysis of massive transaction volumes without real-time processing of every single transaction.

## Scenario (from lesson)

- **Transaction Ingest Agent** — Receives data from online banking, credit card networks, ATMs, wire transfers. Sends raw transactions to batch queue and continues collecting. Does not wait for analysis.

- **Anomaly Scoring Agent** — Periodically polls for transaction batches. When sufficient messages accumulate, processes the batch together: statistical anomalies, unusual patterns, deviations from typical behavior. Assigns fraud risk scores and sends anomaly batch report to queue.

- **Customer Risk Profiling Agent** — Receives anomaly reports. Integrates with customer profiles, historical data, external risk indicators. When significant anomaly data accumulates, re-evaluates risk profiles and generates risk profile report for queue.

- **Regulatory Reporting Agent** — Listens for risk profile reports. Operates on scheduled basis (daily/weekly). Consolidates high-risk data, generates compliance reports and SARs, formats per regulatory standards, submits to authorities.

## Flow

```
Transactions (online, card, ATM, wire)
        ↓
   [BATCH QUEUE]
        ↓
  Anomaly Scoring (batch of 5+)
        ↓
   [BATCH QUEUE]
        ↓
  Risk Profiling (integrates with profiles)
        ↓
   [BATCH QUEUE]
        ↓
  Regulatory Reporting (SAR, compliance)
```

## Setup

```bash
pip install anthropic python-dotenv
```

Set `ANTHROPIC_API_KEY` in `.env`.

## Run

```bash
python main.py
```

## Project Structure

```
financial_fraud_batch/
├── config.py
├── batch_queue/
├── agents/
│   ├── transaction_ingest_agent.py
│   ├── anomaly_scoring_agent.py
│   ├── risk_profiling_agent.py
│   └── regulatory_reporting_agent.py
├── data/transactions.py
├── prompts.py
├── llm_client.py
└── main.py
```
