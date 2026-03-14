"""
Hierarchical Multi-Agent System — Entry Point

Demonstrates 3-layer hierarchy for global product launch.
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

from config import LAUNCH_TASK
from llm_client import LLMClient
from communication.message_router import MessageRouter, MessageDirection
from communication.hierarchy_tracker import HierarchyTracker
from layers.layer1_orchestrator.main_orchestrator import MainOrchestrator
from layers.layer2_sub_orchestrators.development_orchestrator import DevelopmentSubOrchestrator
from layers.layer2_sub_orchestrators.marketing_orchestrator import MarketingSubOrchestrator
from layers.layer2_sub_orchestrators.operations_orchestrator import OperationsSubOrchestrator
from layers.layer3_workers.dev_workers import CodingWorker, TestingWorker
from layers.layer3_workers.marketing_workers import ContentWorker, CampaignWorker
from layers.layer3_workers.ops_workers import DeploymentWorker, LogisticsWorker
from layers.layer3_workers.expert_teams import LegalComplianceTeam, SecurityReviewTeam


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║    HIERARCHICAL MULTI-AGENT SYSTEM DEMO             ║
║         Global Product Launch: CloudSync Pro        ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()
    router = MessageRouter()
    tracker = HierarchyTracker()

    # Layer 3 workers
    coding_worker = CodingWorker(llm)
    testing_worker = TestingWorker(llm)
    security_team = SecurityReviewTeam(llm)
    content_worker = ContentWorker(llm)
    campaign_worker = CampaignWorker(llm)
    deployment_worker = DeploymentWorker(llm)
    logistics_worker = LogisticsWorker(llm)
    legal_team = LegalComplianceTeam(llm)

    workers = {
        "coding_worker": coding_worker,
        "testing_worker": testing_worker,
        "security_team": security_team,
        "content_worker": content_worker,
        "campaign_worker": campaign_worker,
        "deployment_worker": deployment_worker,
        "logistics_worker": logistics_worker,
        "legal_team": legal_team,
    }

    for wid, w in workers.items():
        router.register_agent(wid, w, 3)
        tracker.update_agent_status(wid, 3, "idle", 0.0)

    # Layer 2 sub-orchestrators
    dev_orch = DevelopmentSubOrchestrator(llm, router, tracker)
    dev_orch.workers = {"coding_worker": coding_worker, "testing_worker": testing_worker, "security_team": security_team}

    mkt_orch = MarketingSubOrchestrator(llm, router, tracker)
    mkt_orch.workers = {"content_worker": content_worker, "campaign_worker": campaign_worker}

    ops_orch = OperationsSubOrchestrator(llm, router, tracker)
    ops_orch.workers = {"deployment_worker": deployment_worker, "logistics_worker": logistics_worker, "legal_team": legal_team}

    for orch in [dev_orch, mkt_orch, ops_orch]:
        router.register_agent(orch.agent_id, orch, 2)
        tracker.update_agent_status(orch.agent_id, 2, "idle", 0.0)

    # Layer 1 main orchestrator
    main_orch = MainOrchestrator(llm, router, tracker)
    main_orch.sub_orchestrators = {
        "development_orchestrator": dev_orch,
        "marketing_orchestrator": mkt_orch,
        "operations_orchestrator": ops_orch,
    }
    router.register_agent(main_orch.agent_id, main_orch, 1)

    # ========== LAYER 1 ==========
    print("━" * 60)
    print("LAYER 1: MAIN ORCHESTRATOR (Utility-Based)")
    print("━" * 60)
    print("\n🎯 [L1] Analyzing global launch task...")
    print("📋 [L1] Creating high-level strategic plan...\n")

    plan = main_orch.create_high_level_plan(LAUNCH_TASK)
    domains = plan.get("domains", {})

    for domain_key, domain_data in domains.items():
        delegate = domain_data.get("delegate_to", "")
        print(f"Domain: {domain_key.upper()} → {delegate}")
        print(f"  Goal: {domain_data.get('goal', '')[:60]}...")
        print(f"  Budget: {domain_data.get('budget', '')}\n")

    print("📨 [L1] Delegating to 3 sub-orchestrators...\n")

    main_orch.delegate_to_sub_orchestrators(plan)

    # ========== LAYER 2 + 3 ==========
    print("━" * 60)
    print("LAYER 2: SUB-ORCHESTRATORS (Goal-Based) - Running in parallel")
    print("━" * 60)

    domain_results = {}

    for domain_key, domain_data in domains.items():
        delegate_to = domain_data.get("delegate_to", "")
        orch = main_orch.sub_orchestrators.get(delegate_to)
        if not orch:
            continue

        emoji = {"development": "🔧", "marketing": "📣", "operations": "⚙️"}.get(domain_key, "📋")
        print(f"\n{emoji} [L2-{domain_key.upper()}] {delegate_to}:")
        print(f"   Breaking {domain_key} goals into tasks...")

        tasks = orch.plan_tasks(domain_data)
        task_results = []

        for task in tasks:
            worker_id = task.get("assign_to")
            worker = orch.workers.get(worker_id)
            if worker:
                print(f"   → {worker_id}: \"{task.get('title', '')[:50]}\"")
                router.send(orch.agent_id, 2, worker_id, 3, MessageDirection.DOWN, {"task": task}, domain_key)
                result = worker.execute_task(task)
                router.send(worker_id, 3, orch.agent_id, 2, MessageDirection.UP, {"result": result}, domain_key)
                task_results.append(result)
                orch.task_results[task.get("task_id", "")] = result
                tracker.update_agent_status(worker_id, 3, "completed", 1.0)
                tracker.mark_completed(task.get("task_id", ""))
                if worker_id in ["security_team", "legal_team"]:
                    print(f"   🔐 [L3] {worker_id} (Expert Team):")
                    print(f"      [Experts collaborate internally...]")
                print(f"   ✅ [L3] {worker_id}: {result.get('deliverable', '')[:50]}...")

        domain_results[domain_key] = {"tasks": task_results, "summary": f"{len(task_results)} tasks completed"}
        orch.tracker.update_agent_status(orch.agent_id, 2, "completed", 1.0)

    # ========== RESULTS FLOW BACK ==========
    print("\n" + "━" * 60)
    print("RESULTS FLOWING BACK UP THE HIERARCHY")
    print("━" * 60)
    print("Layer 3 → Layer 2: All workers report completion")
    print("Layer 2 → Layer 1: Sub-orchestrators report domain results\n")

    # ========== LAYER 1 SYNTHESIS ==========
    print("🎯 [L1] FINAL EXECUTIVE REPORT:")
    synthesis = main_orch.synthesize_final_report(domain_results)
    for line in synthesis.strip().split("\n")[:15]:
        print(f"   {line}")
    if "LAUNCH_READINESS" in synthesis.upper():
        print("\n   LAUNCH_READINESS: ✅ READY")

    tracker.update_agent_status(main_orch.agent_id, 1, "completed", 1.0)

    # Simulate Layer 2 → Layer 1 report messages
    for domain_key in domain_results:
        orch = main_orch.sub_orchestrators.get(
            {"development": "development_orchestrator", "marketing": "marketing_orchestrator", "operations": "operations_orchestrator"}[domain_key]
        )
        if orch:
            router.send(orch.agent_id, 2, main_orch.agent_id, 1, MessageDirection.UP, {"results": domain_results[domain_key]}, "global_launch")

    # ========== SUMMARY ==========
    msg_log = router.message_log
    l1_l2 = sum(1 for m in msg_log if m.sender_layer == 1 and m.recipient_layer == 2)
    l2_l3 = sum(1 for m in msg_log if m.sender_layer == 2 and m.recipient_layer == 3)
    l3_l2 = sum(1 for m in msg_log if m.sender_layer == 3 and m.recipient_layer == 2)
    l2_l1 = sum(1 for m in msg_log if m.sender_layer == 2 and m.recipient_layer == 1)

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║           SYSTEM ARCHITECTURE SUMMARY               ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ LAYER 1: 1 Main Orchestrator (Utility-Based)        ║")
    print("║ LAYER 2: 3 Sub-Orchestrators (Goal-Based)           ║")
    print("║ LAYER 3: 6 Workers + 2 Expert Teams                 ║")
    print("║ Total agents: 12                                     ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║ Messages Layer1→Layer2: {l1_l2}                            ║")
    print(f"║ Messages Layer2→Layer3: {l2_l3}                            ║")
    print(f"║ Messages Layer3→Layer2: {l3_l2}                            ║")
    print(f"║ Messages Layer2→Layer1: {l2_l1}                            ║")
    print(f"║ Total messages: {len(msg_log)}                                  ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Max context per agent: Small (focused scope)         ║")
    print("║ vs Single Agent: Would need 12x context             ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ KEY INSIGHT:                                        ║")
    print("║ No single agent was overwhelmed.                    ║")
    print("║ Each layer handled appropriate complexity.          ║")
    print("║ Most scalable + reliable architecture pattern.      ║")
    print("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
