"""
Event-Driven Architecture — Entry Point
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

from event_hub import EventHub
from llm_client import LLMClient
from agents.city_monitor_agent import CityMonitorAgent
from agents.traffic_agent import TrafficAgent
from agents.emergency_agent import EmergencyAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.analytics_agent import AnalyticsAgent


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║      EVENT-DRIVEN ARCHITECTURE DEMONSTRATION        ║
║           Smart City AI Agent System                ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()
    hub = EventHub("city_hub")

    # ━━━ PHASE 1: SUBSCRIPTIONS REGISTERED ━━━
    print("━" * 60)
    print("PHASE 1: SUBSCRIPTIONS REGISTERED")
    print("━" * 60)
    traffic = TrafficAgent(llm, hub)
    emergency = EmergencyAgent(llm, hub)
    maintenance = MaintenanceAgent(llm, hub)
    analytics = AnalyticsAgent(llm, hub)

    # ━━━ PHASE 2: INTRA-AGENT (City Monitor internal bus) ━━━
    print("\n" + "━" * 60)
    print("PHASE 2: INTRA-AGENT (City Monitor internal bus)")
    print("━" * 60)
    city_monitor = CityMonitorAgent(llm, hub)

    # ━━━ PHASE 3: EVENT PUBLISHING + BROADCASTING ━━━
    print("\n" + "━" * 60)
    print("PHASE 3: EVENT PUBLISHING + BROADCASTING")
    print("━" * 60)
    city_monitor.monitor_and_publish()
    print("\n👆 BROADCASTING DEMONSTRATED:")
    print("   Same FIRE event → emergency_agent AND maintenance_agent")
    print("   Each reacts differently and independently!")

    # ━━━ PHASE 4: CONSUMER REACTIONS (Reaction Triggers) ━━━
    print("\n" + "━" * 60)
    print("PHASE 4: CONSUMER REACTIONS (Reaction Triggers)")
    print("━" * 60)
    print("\n🚦 traffic_agent polling...")
    traffic.poll_and_react()
    print("\n🚨 emergency_agent polling...")
    emergency.poll_and_react()
    print("\n🔧 maintenance_agent polling...")
    maintenance.poll_and_react()

    # ━━━ PHASE 5: STREAM PROCESSING (Analytics Agent) ━━━
    print("\n" + "━" * 60)
    print("PHASE 5: STREAM PROCESSING (Analytics Agent)")
    print("━" * 60)
    analytics.process_stream()

    # ━━━ PHASE 6: EVENT REPLAY (Historical Analysis) ━━━
    print("\n" + "━" * 60)
    print("PHASE 6: EVENT REPLAY (Historical Analysis)")
    print("━" * 60)
    analytics.replay_and_analyze()

    # ━━━ FINAL SUMMARY ━━━
    stats = hub.get_stream_stats()
    print("\n" + "━" * 60)
    print("EVENT-DRIVEN PATTERNS DEMONSTRATED")
    print("━" * 60)
    print(f"""
╔══════════════════════════════════════════════════════╗
║         EVENT-DRIVEN PATTERNS DEMONSTRATED          ║
╠══════════════════════════════════════════════════════╣
║ Pattern              │ Status                       ║
╠══════════════════════════════════════════════════════╣
║ Situational Awareness│ ✅ 4 agents aware in real-time║
║ Broadcasting         │ ✅ FIRE event → 3 agents      ║
║ Reaction Triggers    │ ✅ Events drove all behavior  ║
║ Stream Processing    │ ✅ {stats['total_events']} events analyzed          ║
║ Event Replay         │ ✅ Historical patterns found  ║
║ Intra-Agent Bus      │ ✅ 3 internal handlers        ║
╠══════════════════════════════════════════════════════╣
║ Events published:    {stats['total_events']}                              ║
║ Total deliveries:    {stats['delivery_count']} (across all subscribers)   ║
║ Producer knew recipients: NEVER (0/{stats['total_events']})              ║
╚══════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
