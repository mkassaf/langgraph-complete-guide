"""
Event Hub Internals — Entry Point
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

from platform import EventHubPlatform, EventChannel
from llm_client import LLMClient
from agents.sensor_agent import SensorAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.safety_agent import SafetyAgent
from agents.analytics_agent import AnalyticsAgent


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    print("""
╔══════════════════════════════════════════════════════╗
║         EVENT HUB INTERNALS DEMONSTRATION           ║
║    All 5 Components + Broker Node in Action         ║
╚══════════════════════════════════════════════════════╝
""")

    llm = LLMClient()
    platform = EventHubPlatform("factory_hub")

    # ━━━ SETUP: REGISTRATIONS ━━━
    print("━" * 60)
    print("SETUP: REGISTRATIONS")
    print("━" * 60)
    platform.register_publisher("sensor_agent", list(EventChannel))
    maintenance = MaintenanceAgent(llm, platform)
    safety = SafetyAgent(llm, platform)
    analytics = AnalyticsAgent(llm, platform)

    # maintenance and analytics start polling (ready for events)
    platform.consumer_starts_polling("maintenance_agent")
    platform.consumer_starts_polling("analytics_agent")
    # safety_agent starts OFFLINE - will come online later

    # ━━━ EVENT 1: FULL PUBLISH FLOW ━━━
    print("\n" + "━" * 60)
    print("EVENT 1: FULL PUBLISH FLOW")
    print("━" * 60)
    sensor = SensorAgent(llm, platform)
    sensor.publish_events(platform)

    # ━━━ CONSUMER REACTIONS ━━━
    print("\n" + "━" * 60)
    print("CONSUMER REACTIONS")
    print("━" * 60)
    maintenance.poll_and_react()
    safety.poll_and_react()

    # ━━━ BATCH STREAM PROCESSING ━━━
    print("\n" + "━" * 60)
    print("BATCH STREAM PROCESSING")
    print("━" * 60)
    analytics.process_batch()

    # ━━━ EVENT REPLAY ━━━
    print("\n" + "━" * 60)
    print("EVENT REPLAY (Long-term storage value)")
    print("━" * 60)
    analytics.replay_and_analyze()

    # ━━━ FINAL STATUS ━━━
    platform.print_platform_status()


if __name__ == "__main__":
    main()
