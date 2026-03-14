"""
Financial Fraud & Risk — Batch Processing Example

Large financial company: transaction monitoring, fraud detection, risk assessment.
Batch queue enables efficient analysis of massive transaction volumes.

Flow:
  1. Transaction Ingest → raw transactions to queue (doesn't wait)
  2. Anomaly Scoring → polls for batch, assigns fraud scores, sends report
  3. Risk Profiling → integrates anomaly data with profiles, sends risk report
  4. Regulatory Reporting → consolidates, generates SAR/compliance, submits
"""

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from dotenv import load_dotenv

_env_path = os.path.join(_SCRIPT_DIR, "..", "..", ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
else:
    load_dotenv()

from batch_queue import BatchQueue
from llm_client import LLMClient
from agents import (
    TransactionIngestAgent,
    AnomalyScoringAgent,
    RiskProfilingAgent,
    RegulatoryReportingAgent,
)
from data.transactions import SAMPLE_TRANSACTIONS, CUSTOMER_PROFILES


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║   FINANCIAL FRAUD & RISK — BATCH PROCESSING        ║
║   Transaction monitoring • Anomaly scoring          ║
║   Risk profiling • Regulatory reporting             ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()

    # Queues: transactions → anomaly reports → risk reports
    txn_queue = BatchQueue("transactions")
    anomaly_queue = BatchQueue("anomaly_reports")
    risk_queue = BatchQueue("risk_reports")

    # Agents
    ingest = TransactionIngestAgent(llm, txn_queue)
    anomaly = AnomalyScoringAgent(llm, txn_queue, anomaly_queue)
    risk = RiskProfilingAgent(llm, anomaly_queue, risk_queue, CUSTOMER_PROFILES)
    regulatory = RegulatoryReportingAgent(llm, risk_queue)

    # ━━━ STAGE 1: Ingest (Producer) ━━━
    print("━" * 60)
    print("STAGE 1: TRANSACTION INGEST")
    print("━" * 60)
    ingest.ingest_and_submit(SAMPLE_TRANSACTIONS)

    # ━━━ STAGE 2: Anomaly Scoring ━━━
    print("\n" + "━" * 60)
    print("STAGE 2: ANOMALY SCORING")
    print("━" * 60)
    anomaly.poll_and_score()

    # ━━━ STAGE 3: Risk Profiling ━━━
    print("\n" + "━" * 60)
    print("STAGE 3: CUSTOMER RISK PROFILING")
    print("━" * 60)
    risk.poll_and_profile()

    # ━━━ STAGE 4: Regulatory Reporting ━━━
    print("\n" + "━" * 60)
    print("STAGE 4: REGULATORY REPORTING")
    print("━" * 60)
    regulatory.poll_and_report()

    # ━━━ SUMMARY ━━━
    print("\n" + "━" * 60)
    print("BATCH PROCESSING FLOW COMPLETE")
    print("━" * 60)
    print("""
╔══════════════════════════════════════════════════════╗
║          FRAUD & RISK BATCH FLOW                     ║
╠══════════════════════════════════════════════════════╣
║ Transaction Ingest:   Raw data → queue (no wait)    ║
║ Anomaly Scoring:      Batch analysis, fraud scores  ║
║ Risk Profiling:       Profile updates, risk report  ║
║ Regulatory:           SAR, compliance, submission  ║
╠══════════════════════════════════════════════════════╣
║ Deep analysis doesn't need real-time per txn.       ║
║ Batch processing enables efficient volume handling. ║
╚══════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
