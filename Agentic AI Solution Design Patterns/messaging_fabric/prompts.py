"""
Prompts for Messaging Fabric — Smart Factory.
"""

PRODUCTION_PROMPT = """
You are a production agent receiving a factory order.

Order from message queue:
{order}

Decide:
PRODUCTION_PLAN: [how to fulfill this order]
ESTIMATED_TIME: [production time estimate]
QUALITY_CHECKS_NEEDED: [what to check]
EVENTS_TO_PUBLISH: [any events to broadcast]
"""

SAFETY_MONITOR_PROMPT = """
You are a safety monitoring agent.

Current sensor readings:
{readings}

Analyze each reading. For each anomaly found:
EVENT_TYPE: overheat/abnormal_vibration/pressure_spike
SEVERITY: warning/critical
AFFECTED_MACHINE: [machine id]
DESCRIPTION: [what's wrong]
RECOMMENDED_ACTION: [what should happen]

If all normal: STATUS: all_systems_normal
"""

MAINTENANCE_RESPONSE_PROMPT = """
You are a maintenance agent.

Safety event received:
{event}

Determine response:
URGENCY: immediate/scheduled/monitor
MAINTENANCE_TASK: [what needs to be done]
ESTIMATED_DOWNTIME: [how long machine will be offline]
PARTS_NEEDED: [any parts required]
NOTIFY: [who needs to know]
"""

BATCH_REPORT_PROMPT = """
You are a reporting agent analyzing a shift's quality data.

Batch of quality checks ({count} items):
{batch_items}

Generate comprehensive shift report:
TOTAL_ITEMS_INSPECTED: [number]
PASS_RATE: [percentage]
DEFECTS_FOUND: [list of defect types and counts]
TRENDS: [any patterns noticed]
RECOMMENDATIONS: [improvements for next shift]
CRITICAL_ISSUES: [anything requiring immediate attention]
"""
