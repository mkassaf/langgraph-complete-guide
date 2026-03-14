"""
Prompts for Planning pattern — decomposition, workers, synthesis.
"""

DECOMPOSITION_PROMPT = """
You are an orchestrator agent planning a large event.

Task to plan:
{task_description}

Available worker agents:
- venue_worker: Books event venues
- registration_worker: Sets up registration system
- catering_worker: Arranges food and beverage
- speakers_worker: Coordinates keynote speakers
- marketing_worker: Creates promotional campaign

Break this into work units. For each unit specify:
UNIT_ID: [unique id like "unit_001"]
TITLE: [short title]
ASSIGNED_TO: [venue_worker|registration_worker|catering_worker|speakers_worker|marketing_worker]
DESCRIPTION: [what the worker needs to do]
REQUIREMENTS: [specific requirements, one per line]
DEPENDS_ON: [unit_ids this must wait for, comma-separated, or "none"]

Create 5 work units - one for each worker type.
Consider dependencies: venue must be confirmed before catering and speakers.
Registration and marketing can run in parallel with venue.
Format each unit clearly. End with EXECUTION_ORDER: [comma-separated unit_ids]
"""

WORKER_PROMPT = """
You are a specialized {worker_type} agent.
Complete this work unit:

Task: {unit_description}
Requirements: {requirements}
Context from completed dependencies: {dependency_results}

Provide detailed results in this format:
STATUS: completed
OUTPUT: [structured results - venue name, costs, details as appropriate]
SUMMARY: [brief summary for orchestrator]
RECOMMENDATIONS: [any suggestions]
"""

SYNTHESIS_PROMPT = """
You are an orchestrator agent.
All worker agents have completed their tasks.
Synthesize their results into a coherent final plan.

Worker Results:
{all_results}

Create a comprehensive conference plan:
EXECUTIVE_SUMMARY: [overview]
VENUE: [confirmed details]
SCHEDULE: [2-day agenda]
CATERING: [meal plan]
SPEAKERS: [lineup]
REGISTRATION: [system details]
MARKETING: [campaign plan]
BUDGET_BREAKDOWN: [cost allocation]
NEXT_STEPS: [immediate actions needed]
"""
