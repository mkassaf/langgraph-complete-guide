"""
Reaction Triggers Demo — Events drive behavior.
"""


def run_reaction_triggers(traffic_agent, emergency_agent, maintenance_agent):
    """Consumers poll and react to events."""
    traffic_agent.poll_and_react()
    emergency_agent.poll_and_react()
    maintenance_agent.poll_and_react()
