"""
Prompts for planning patterns.
"""

PLANNER_PROMPT = """
You are a planning agent. Create a COMPLETE step-by-step plan
for this task before any actions are taken.

Task: {task}

Available tools: check_availability, search_venues, get_catering, create_proposal

Generate complete plan. Reply in this format:
STEP_1: check_availability(team_size=15, month="next month") - confirm team availability
STEP_2: search_venues(capacity=15, dates=[available dates]) - find venues
STEP_3: get_catering(guests=15, venue=chosen, date=chosen) - get catering options
STEP_4: create_proposal(details=all above) - create final proposal

List each step with tool name and parameters.
EXECUTION_ORDER: sequential
"""

DEPENDENCY_ANALYSIS_PROMPT = """
Analyze these plan steps for dependencies:

{steps}

For each step identify:
- DEPENDS_ON: which step IDs must complete first (or "none")
- CAN_PARALLEL_WITH: which steps can run at same time

Format:
STEP_1 (check_availability): DEPENDS_ON=none, CAN_PARALLEL=STEP_2
STEP_2 (search_venues): DEPENDS_ON=none, CAN_PARALLEL=STEP_1
STEP_3 (get_catering): DEPENDS_ON=STEP_1,STEP_2
STEP_4 (create_proposal): DEPENDS_ON=STEP_3
"""

REASONING_NO_OBS_PROMPT = """
Before calling ANY tools, complete all reasoning for this task.
Identify EVERY piece of data you need and how you'll use it.

Task: {task}

Complete your reasoning. DO NOT call any tools yet.
MAIN_PLAN: [high-level steps]
DATA_NEEDED:
  QUERY_1: check_availability(team_size=15, month=next) → purpose: get available dates
  QUERY_2: search_venues(capacity=15, dates=from_query_1) → purpose: find venues
  QUERY_3: get_catering(guests=15, venue=X, date=Y) → purpose: catering options
SYNTHESIS: Combine dates + venues + catering into final proposal
"""

CRITIC_PROMPT = """
You are a CRITIC agent evaluating a meeting planning proposal.

Plan to evaluate:
{plan}

Assess against these criteria:
1. Are all attendees confirmed before venue booking?
2. Is budget ($2000) explicitly checked?
3. Are venue availability pre-checks included?
4. Is there a backup option?
5. Are all constraints (15 people, engaging activities, catering) addressed?

For each issue found:
ISSUE: [description]
SEVERITY: minor/major/critical
SUGGESTION: [how to fix]

QUALITY_SCORE: [0.0 to 1.0]
APPROVED: yes/no (yes if score >= 0.85)
"""

REFINER_PROMPT = """
You are a REFINER agent. Improve this plan based on critic feedback.

Original plan: {plan}
Critic feedback: {feedback}

Produce improved plan addressing ALL issues:
CHANGES_MADE: [list of changes]
REFINED_PLAN:
STEP_1: ...
STEP_2: ...
QUALITY_IMPROVEMENTS: [what was fixed]
"""
