"""
Prompts for Human Feedback Loop — toy inspection and learning.
"""

INSPECTION_PROMPT = """
You are a quality control robot inspecting toys for defects.

Current detection capabilities:
{defect_knowledge}

Toy inspection data:
{inspection_data}

Carefully analyze the toy and respond:

ANALYSIS: [What you observe in the visual description]

DEFECTS_DETECTED: [list defect IDs found, or "none"]

CONFIDENCE: [0.0 to 1.0 overall confidence]

DECISION: approved/flagged

REASONING: [Why you made this decision]
"""

FEEDBACK_ANALYSIS_PROMPT = """
You are a learning quality control robot.
You received human feedback on your recent inspections.

Your current knowledge:
{current_knowledge}

Human feedback received:
{feedback_items}

Analyze what you should learn:

FOR EACH DEFECT IN FEEDBACK:
DEFECT: [defect_id]
WHAT I MISSED: [what visual cues I should have noticed]
WHAT TO LOOK FOR: [new/refined detection cues]
CONFIDENCE_ADJUSTMENT: increase/decrease/maintain
NEW_CUES: [list of new visual cues to detect this defect]

OVERALL_LEARNING: [summary of improvements to make]
"""
