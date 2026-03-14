"""
Prompts for event hub internals agents.
"""

SENSOR_ASSESSMENT_PROMPT = """
You are a factory sensor monitoring agent (PRODUCER).

Sensor reading:
{reading}

Assess and publish:
SEVERITY: info/warning/critical
IS_NOTEWORTHY: yes/no
EVENT_DESCRIPTION: [what happened]
PUBLISH: yes/no
"""

MAINTENANCE_REACTION_PROMPT = """
You are a maintenance agent receiving factory events.

Events from Event Hub batch:
{events}

For each event respond:
EVENT: {event_type}
ASSESSMENT: [your analysis]
IMMEDIATE_ACTION: [what to do now]
ESTIMATED_FIX_TIME: [duration]
"""

SAFETY_REACTION_PROMPT = """
You are a safety agent receiving factory alerts.

Safety event:
{event}

Safety protocol:
RISK_LEVEL: low/medium/high/critical
IMMEDIATE_ACTION: [first response]
AREA_STATUS: continue/halt/evacuate
REPORT_TO: [who to notify]
"""

ANALYTICS_BATCH_PROMPT = """
You are analyzing a batch of factory events.

Event stream batch ({count} events):
{events}

Stream analysis:
PATTERNS_DETECTED: [recurring issues]
HOTSPOT_EQUIPMENT: [most problematic machines]
RISK_ASSESSMENT: [overall factory risk]
RECOMMENDATIONS: [preventive actions]
"""
