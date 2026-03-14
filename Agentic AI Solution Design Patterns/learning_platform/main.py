"""
Event-Driven Learning Platform — Entry Point

4 agents, central event hub, NO direct agent-to-agent communication.
Events drive ALL system behavior.
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

from event_hub import LearningEventHub, LearningEventType
from llm_client import LLMClient
from agents import (
    UserActivityAgent,
    PerformanceAnalysisAgent,
    ContentRecommendationAgent,
    AdaptiveInterfaceAgent,
)
from data.student_data import STUDENT_ACTIVITIES, THRESHOLDS
from data.content_library import CONTENT_LIBRARY, PEER_BENCHMARKS


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║    EVENT-DRIVEN LEARNING PLATFORM SCENARIO          ║
║         4 AI Agents + Central Event Hub             ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()
    hub = LearningEventHub()

    # ━━━ SETUP: SUBSCRIPTIONS ━━━
    print("━" * 60)
    print("SETUP: SUBSCRIPTIONS")
    print("━" * 60)
    print("[EVENT HUB] user_activity_agent: NO subscriptions (producer only)")
    user_activity = UserActivityAgent(llm, hub)
    performance = PerformanceAnalysisAgent(llm, hub)
    content = ContentRecommendationAgent(llm, hub)
    interface = AdaptiveInterfaceAgent(llm, hub)
    print()

    # ━━━ MONITOR ACTIVITIES (Producer) ━━━
    print("━" * 60)
    print("MONITORING STUDENT ACTIVITIES")
    print("━" * 60)
    for activity in STUDENT_ACTIVITIES:
        name = activity.get("name", activity.get("student_id", "?"))
        print(f"\n📊 user_activity_agent monitoring {name}...")
        published = user_activity.monitor_student_activity(activity, THRESHOLDS)
        if published:
            print("✓ user_activity_agent continues monitoring")
        else:
            print("✓ No significant event (below threshold)")

    # ━━━ CONSUMER CHAIN: ① → ② → ③ ━━━
    print("\n" + "━" * 60)
    print("CONSUMER CHAIN: ① → ② → ③")
    print("━" * 60)

    print("\n📈 performance_agent polling for EVENT ①...")
    perf_events = performance.poll_and_analyze(STUDENT_ACTIVITIES, PEER_BENCHMARKS)
    for _ in perf_events:
        print("   ✓ Analyzed, published EVENT ②")

    print("\n📚 content_agent polling for EVENT ②...")
    content_events = content.poll_and_recommend(CONTENT_LIBRARY)
    for _ in content_events:
        print("   ✓ Recommended, published EVENT ③")

    print("\n🖥️  interface_agent polling for EVENT ② and ③...")
    interface_events = interface.poll_and_adapt()
    print(f"   ✓ Reacted to {interface_events} events")

    # ━━━ DASHBOARDS ━━━
    print("\n" + "━" * 60)
    print("PERSONALIZED DASHBOARDS")
    print("━" * 60)
    student_ids = sorted({a.get("student_id") for a in STUDENT_ACTIVITIES if a.get("student_id")})
    for sid in student_ids:
        activities = [a for a in STUDENT_ACTIVITIES if a.get("student_id") == sid]
        name = activities[0].get("name", sid) if activities else sid
        print(f"\n{name} ({sid}):")
        if sid in interface.dashboard_state:
            state = interface.dashboard_state[sid]
            if "skill_gap_reaction" in state:
                print("  [Skill gap reaction]")
                for line in state["skill_gap_reaction"].strip().split("\n")[:6]:
                    print(f"    {line}")
            if "recommendations_reaction" in state:
                print("  [Recommendations]")
                for line in state["recommendations_reaction"].strip().split("\n")[:6]:
                    print(f"    {line}")
        else:
            print("  (No dashboard updates)")

    # ━━━ EVENT CHAIN SUMMARY ━━━
    print("\n" + "━" * 60)
    print("EVENT CHAIN SUMMARY")
    print("━" * 60)
    total_events = len(hub._event_stream)
    total_deliveries = len(hub.delivery_log)
    print(f"""
╔══════════════════════════════════════════════════════╗
║           EVENT-DRIVEN SCENARIO RESULTS             ║
╠══════════════════════════════════════════════════════╣
║ Students processed:     {len(student_ids)}                           ║
║ Events published:       {total_events} (①→②→③ per student)        ║
║ Total deliveries:       {total_deliveries}                         ║
╠══════════════════════════════════════════════════════╣
║ Agent communications:                                ║
║   Direct agent-to-agent:     0 ← KEY INSIGHT        ║
║   Via Event Hub only:        {total_deliveries}                    ║
╠══════════════════════════════════════════════════════╣
║ KEY INSIGHT:                                         ║
║ ALL system behavior was driven by events.            ║
║ No agent ever called another agent directly.         ║
║ Adding a new agent = just subscribe to events.        ║
╚══════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
