"""
Crisis orchestrator — delegates breach response to expert team.
"""


class CrisisOrchestrator:
    """
    Orchestrator that delegates breach response as ONE subtask.
    Sees expert team as a single worker.
    """

    def __init__(self, expert_team_entry_point):
        self.entry_point = expert_team_entry_point

    def handle_breach(self, incident: str) -> dict:
        """
        Delegates to breach_response_worker (entry point).
        Receives unified response.
        """
        return self.entry_point.process_task(incident)
