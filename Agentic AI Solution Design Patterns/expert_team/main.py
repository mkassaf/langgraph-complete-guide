"""
Specialized Expert Team — Entry Point

Demonstrates expert team pattern for cybersecurity breach response.
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

from config import BREACH_SCENARIO
from llm_client import LLMClient
from expert_team.entry_point import ExpertTeamEntryPoint
from orchestrator.crisis_orchestrator import CrisisOrchestrator


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║      SPECIALIZED EXPERT TEAM PATTERN DEMO            ║
║         Cybersecurity Breach Response               ║
╚══════════════════════════════════════════════════════╝
""")

    print("━" * 60)
    print("FROM ORCHESTRATOR'S PERSPECTIVE")
    print("━" * 60)
    print("\n🎯 Crisis Orchestrator received: SECURITY BREACH ALERT")
    print("📨 Delegating to: breach_response_worker (entry point)")
    print("[Orchestrator sees ONE worker, not 4 experts]\n")

    llm = LLMClient()
    entry_point = ExpertTeamEntryPoint(llm)
    orchestrator = CrisisOrchestrator(entry_point)

    print("━" * 60)
    print("INSIDE THE EXPERT TEAM")
    print("━" * 60)

    result = orchestrator.handle_breach(BREACH_SCENARIO)

    # Display Round 0 (initial analyses)
    print("\nROUND 0: INITIAL INDEPENDENT ANALYSES")
    print("─" * 40)
    emojis = {
        "threat_analyst": "🔐",
        "network_expert": "🌐",
        "legal_advisor": "⚖️",
        "comms_manager": "📣",
    }
    for a in result.get("expert_analyses", []):
        print(f"\n{emojis.get(a.expert_id, '📋')} {a.expert_id}:")
        for f in a.findings[:3]:
            print(f"   \"{f}\"")
        print(f"   Confidence: {a.confidence:.2f}")

    # Display collaboration rounds
    for cr in result.get("collaboration_rounds", []):
        print(f"\nROUND {cr.round_number}: EXPERT DEBATE")
        print("─" * 40)
        for m in cr.messages[:6]:
            msg_type = "CHALLENGE" if m.message_type.value == "challenge" else "SUPPORT" if m.message_type.value == "support" else "NEW_FINDING"
            target = f" → {m.recipient_expert}" if m.recipient_expert else " (broadcast)"
            print(f"💬 {m.sender_expert} {msg_type}{target}:")
            print(f"   {m.content[:100]}...")
        if cr.agreed_points:
            print(f"\n✅ Consensus emerging on: {len(cr.agreed_points)} points")
        if cr.disputed_points:
            print(f"⚠️  Still disputed: {len(cr.disputed_points)} points")

    # Consensus
    consensus = result.get("consensus")
    if consensus:
        print("\n" + "━" * 60)
        print("CONSENSUS RESPONSE SENT TO ORCHESTRATOR")
        print("━" * 60)
        print("\nIMMEDIATE ACTIONS (next 6 hours):")
        for i, a in enumerate(consensus.immediate_actions[:5], 1):
            print(f"  {i}. {a}")
        print("\nSHORT TERM ACTIONS (24-72 hours):")
        for i, a in enumerate(consensus.short_term_actions[:5], 1):
            print(f"  {i}. {a}")
        if consensus.dissenting_opinions:
            print(f"\nDissenting: {consensus.dissenting_opinions}")

    msg_count = result.get("message_count", 0)
    challenges = sum(
        1
        for cr in result.get("collaboration_rounds", [])
        for m in cr.messages
        if m.message_type.value == "challenge"
    )

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║              TEAM COLLABORATION SUMMARY             ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Experts involved:         4                         ║")
    print(f"║ Collaboration rounds:     {len(result.get('collaboration_rounds', []))}                         ║")
    print(f"║ Total messages exchanged: {msg_count}                        ║")
    print(f"║ Challenges issued:        {challenges}                         ║")
    print(f"║ Final consensus: REACHED (confidence: {consensus.confidence_level:.2f})        ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ FROM ORCHESTRATOR VIEW:                             ║")
    print("║ Saw: 1 worker, 1 task, 1 result                    ║")
    print(f"║ Reality: 4 experts, {len(result.get('collaboration_rounds', []))} debate rounds, {msg_count} messages   ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ KEY INSIGHT:                                        ║")
    print("║ Expert team produced a response that NO single     ║")
    print("║ agent could have created - it required deep        ║")
    print("║ domain expertise AND cross-domain collaboration.   ║")
    print("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
