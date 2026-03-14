"""
Individual agent memory — private memory system.
"""

from memory.memory_types import AgentMemoryState


class AgentMemory:
    """
    Individual agent's private memory system.

    Agent ALSO writes important updates to SharedMemorySystem.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state = AgentMemoryState(
            agent_id=agent_id,
            current_objective="",
            recent_actions=[],
            observations=[],
        )

    def update_objective(self, objective: str):
        """Update what agent is currently trying to do."""
        self.state.current_objective = objective

    def record_action(self, action: str, result: str):
        """Log action taken and its result."""
        self.state.recent_actions.append(f"{action} → {result}")
        if len(self.state.recent_actions) > 10:
            self.state.recent_actions = self.state.recent_actions[-10:]

    def record_observation(self, observation: str):
        """Log something observed about environment."""
        self.state.observations.append(observation)
        if len(self.state.observations) > 10:
            self.state.observations = self.state.observations[-10:]

    def write_to_scratchpad(self, key: str, value):
        """Temporary computation storage."""
        self.state.scratchpad[key] = value

    def get_context_summary(self) -> str:
        """Summary of agent's current state for LLM prompt."""
        return (
            f"Objective: {self.state.current_objective}\n"
            f"Recent actions: {self.state.recent_actions[-5:]}\n"
            f"Observations: {self.state.observations[-5:]}"
        )
