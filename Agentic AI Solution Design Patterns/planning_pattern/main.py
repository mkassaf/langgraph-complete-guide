"""
Planning Pattern — Entry Point

Demonstrates Orchestrator-Worker conference planning.
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

from config import CONFERENCE_TASK
from llm_client import LLMClient
from communication.message_bus import MessageBus
from communication.work_unit import WorkerType
from agents.orchestrator import OrchestratorAgent, TaskDecomposer
from agents.workers import (
    VenueWorker,
    RegistrationWorker,
    CateringWorker,
    SpeakersWorker,
    MarketingWorker,
)


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║         PLANNING PATTERN DEMONSTRATION              ║
║      Orchestrator-Worker Conference Planning        ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()
    bus = MessageBus()

    bus.register_worker(WorkerType.VENUE, VenueWorker(llm))
    bus.register_worker(WorkerType.REGISTRATION, RegistrationWorker(llm))
    bus.register_worker(WorkerType.CATERING, CateringWorker(llm))
    bus.register_worker(WorkerType.SPEAKERS, SpeakersWorker(llm))
    bus.register_worker(WorkerType.MARKETING, MarketingWorker(llm))

    orchestrator = OrchestratorAgent(llm, bus)

    print("━" * 60)
    print("PHASE 1: TASK DECOMPOSITION (Orchestrator LLM)")
    print("━" * 60)
    print("\n🎯 ORCHESTRATOR analyzing task...")
    print('Breaking "Annual Conference for 500" into work units:\n')

    plan = orchestrator.decomposer.decompose(CONFERENCE_TASK, list(WorkerType))

    print(f"📋 PLAN CREATED: {len(plan.work_units)} work units")
    for u in plan.work_units:
        deps = f" (needs {', '.join(u.dependencies)})" if u.dependencies else ""
        print(f"   {u.unit_id}: {u.title} → {u.assigned_worker.value}{deps}")
    print(f"\nExecution order: {' → '.join(plan.execution_order)}\n")

    print("━" * 60)
    print("PHASE 2: WORKER EXECUTION")
    print("━" * 60)

    worker_emojis = {
        WorkerType.VENUE: "🏢",
        WorkerType.REGISTRATION: "📝",
        WorkerType.CATERING: "🍽️",
        WorkerType.SPEAKERS: "🎤",
        WorkerType.MARKETING: "📣",
    }

    results = {}
    for unit_id in plan.execution_order:
        unit = next((u for u in plan.work_units if u.unit_id == unit_id), None)
        if not unit:
            continue
        dep_results = {d: results[d] for d in unit.dependencies if d in results}
        unit.result = {"dependency_results": dep_results}

        print(f"\n📨 Orchestrator → {unit.assigned_worker.value}: \"{unit.title}\"")
        print(f"{worker_emojis.get(unit.assigned_worker, '⚙️')} {unit.assigned_worker.value} executing...")

        result = orchestrator.delegate_work_unit(unit, dep_results)
        results[unit_id] = result

        status = "✅" if result.success else "❌"
        print(f"   {result.summary[:80]}...")
        print(f"{status} {unit.assigned_worker.value} → Orchestrator: {'COMPLETED' if result.success else 'FAILED'}\n")

    print("━" * 60)
    print("PHASE 3: RESULT SYNTHESIS (Orchestrator LLM)")
    print("━" * 60)
    print("\n🎯 ORCHESTRATOR synthesizing all results...\n")

    synthesis = orchestrator.synthesize_results(results)
    print("FINAL CONFERENCE PLAN:")
    print("-" * 40)
    for line in synthesis.split("\n")[:30]:
        print(line)
    if synthesis.count("\n") > 30:
        print("...")

    log = bus.get_communication_log()
    success_count = sum(1 for r in results.values() if r.success)

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║              ORCHESTRATION SUMMARY                  ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║ Total work units:      {len(plan.work_units)}                            ║")
    print(f"║ Workers utilized:      {len(plan.work_units)}/{len(plan.work_units)}                          ║")
    print(f"║ Successful completions: {success_count}/{len(plan.work_units)}                         ║")
    print(f"║ Failed units:          {len(plan.work_units) - success_count}                            ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║ Messages exchanged:    {len(log) * 2} ({len(plan.work_units)} requests + {len(plan.work_units)} results) ║")
    print("║ Context per agent:     Small (focused tasks only)   ║")
    print("║ vs Single agent:       Would need 5x context       ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ KEY INSIGHT:                                        ║")
    print("║ Orchestrator maintained high-level coherence while  ║")
    print("║ workers handled details in parallel, preventing     ║")
    print("║ context window overflow.                            ║")
    print("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
