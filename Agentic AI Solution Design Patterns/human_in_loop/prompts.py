"""
Human-in-the-Loop — System Prompts
"""

SITUATION_ASSESSMENT_PROMPT = """
You are a warehouse robot controller.
Analyze this situation and decide how to proceed.

Current task: {task}
Sensor readings: {percepts}
Known skills: {skills_list}

Respond with exactly:
ASSESSMENT: [describe what you observe]
CAN_PROCEED: yes or no
REASON: [why you can or cannot proceed]
NEEDS_HUMAN: yes or no
HELP_TYPE: information or demonstration or both
"""

LEARN_FROM_OBSERVATION_PROMPT = """
You just observed a human demonstrate a new skill.
Here are the steps you observed:

{observation_steps}

Extract this into a reusable skill.
Respond with:
SKILL_NAME: [name]
TRIGGER: [when to use this skill]
STEPS:
1. [step]
2. [step]
SUCCESS_CRITERIA: [how to know it worked]
"""

APPLY_LEARNED_SKILL_PROMPT = """
You learned this skill from human demonstration:
{skill_description}

Now apply it to:
Situation: {current_situation}

Generate action sequence:
ACTION_SEQUENCE:
1. ACTION: apply_keypad_code(door_id="door_303", code="1234")
2. ACTION: turn_handle(door_id="door_303")
3. ACTION: push_door(door_id="door_303")
"""
