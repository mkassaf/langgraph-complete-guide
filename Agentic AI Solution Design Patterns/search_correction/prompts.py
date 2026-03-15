"""Prompts for search and self-correction patterns."""

LATS_GENERATE_ACTIONS_PROMPT = """
You are a planning agent using LATS (Language Agent Tree Search).

Current task: {task}
Current state: {state}

Generate 3 DIVERSE candidate next actions. Each a different approach.

ACTION_A:
  action: [tool_call or step]
  thought: [reasoning]
  predicted_success: [0.0-1.0]

ACTION_B:
  action: [different approach]
  thought: [reasoning]
  predicted_success: [0.0-1.0]

ACTION_C:
  action: [another approach]
  thought: [reasoning]
  predicted_success: [0.0-1.0]
"""

LATS_EVALUATE_PROMPT = """
Evaluate this hypothetical action for meeting planning:

Action: {action}
Context: {context}

Simulate the full outcome:
PREDICTED_OUTCOME: [what would happen]
RISKS: [what could go wrong]
SUCCESS_PROBABILITY: [0.0 to 1.0]
SCORE_REASONING: [why this score]
"""

DISCOVERY_PROMPT = """
You are performing META-REASONING. Do NOT solve the task.
Generate the OPTIMAL REASONING STRUCTURE for this type of task.

Task: {task}

Generate custom reasoning rules:
REASONING_RULE_1: [constraint or ordering rule]
REASONING_RULE_2: [constraint or ordering rule]
REASONING_RULE_3: [constraint or ordering rule]
REASONING_RULE_4: [constraint or ordering rule]
REASONING_RULE_5: [constraint or ordering rule]

Focus on: ordering, dependencies, validation, risk mitigation.
"""

EXECUTION_WITH_RULES_PROMPT = """
Solve this task. You MUST follow these reasoning rules:

{reasoning_rules}

Task: {task}
Available tools: check_availability, search_venues, get_catering

Show which rule guides each decision:
STEP 1 [Rule X]: action...
STEP 2 [Rule Y]: action...
"""

PLANNER_PROMPT = """
Create a detailed plan for this meeting:
{task}

AGENDA:
1. [time] - [item]
2. [time] - [item]
...

VENUE_CHOICE: [venue name]
CATERER: [caterer name]
BUDGET_BREAKDOWN: [costs]
"""

VERIFIER_PROMPT = """
You are a VERIFIER AGENT with an INDEPENDENT LLM.
Evaluate this meeting plan for errors and compliance.

Plan: {plan}

Check each criterion:

1. LOGICAL_SEQUENCE: Is agenda in correct order? (kickoff before lunch)
2. VENDOR_COMPLIANCE: Are all vendors on approved list? Use compliance_checker.
3. FACTUAL_ACCURACY: Are dates, times, capacities correct?
4. COMPLETENESS: Budget check, attendance confirmation present?

For each check:
CHECK: [name]
RESULT: pass/fail
SEVERITY: fatal/minor (if fail)
ISSUE: [description if fail]

OVERALL_VERDICT: pass/fail
"""
