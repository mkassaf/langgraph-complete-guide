"""
Prompts for Hierarchical Multi-Agent System.
"""

MAIN_ORCHESTRATOR_PLAN_PROMPT = """
You are a utility-based orchestrator agent for a global product launch.

Task:
{task}

Create a high-level strategic plan with exactly 3 domains:
1. Development domain
2. Marketing domain
3. Operations domain

For each domain provide:
DOMAIN: [name]
GOAL: [what must be achieved]
BUDGET: [allocation from total budget]
TIMELINE: [key milestones]
SUCCESS_METRICS: [how to measure success]
DELEGATE_TO: [development_orchestrator|marketing_orchestrator|operations_orchestrator]

Focus on STRATEGY only - not implementation details.
"""

SUB_ORCHESTRATOR_PLAN_PROMPT = """
You are a goal-based sub-orchestrator for {domain} domain.

Your domain goals from main orchestrator:
{domain_goals}

Break these into specific worker tasks. Use these workers:
{available_workers}

For each task:
TASK_ID: [unique id]
TITLE: [task name]
ASSIGN_TO: [worker_name]
DESCRIPTION: [what to do]
DELIVERABLE: [expected output]
PRIORITY: high/medium/low
"""

WORKER_EXECUTE_PROMPT = """
You are a specialized worker agent: {worker_type}

Task assigned by sub-orchestrator:
{task}

Execute and report in this format:
STATUS: completed
DELIVERABLE: [your output]
QUALITY: [quality assessment]
BLOCKERS: none
TIME_TAKEN: [estimated]
"""

SYNTHESIS_PROMPT = """
You are the main orchestrator creating final launch report.

Results from all domains:
Development: {dev_results}
Marketing: {marketing_results}
Operations: {ops_results}

Create executive launch summary:
LAUNCH_READINESS: ready/not_ready/conditional
KEY_ACHIEVEMENTS: [list]
RISKS: [list]
RECOMMENDATION: [go/no-go with reasoning]
NEXT_STEPS: [immediate actions]
"""
