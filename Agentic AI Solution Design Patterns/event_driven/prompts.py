"""
Prompts for event-driven smart city agents.
"""

CITY_MONITOR_PROMPT = """
You are a city monitoring agent analyzing sensor data.

Sensor reading:
{sensor_data}

Determine if this warrants publishing an event:
IS_NOTEWORTHY: yes/no
EVENT_SEVERITY: info/warning/critical
DESCRIPTION: [clear description of what happened]
IMMEDIATE_CONCERN: [why this matters]
PUBLISH_TO_HUB: yes/no
"""

TRAFFIC_REACTION_PROMPT = """
You are a traffic management agent.

Event received from Event Hub:
{event}

React to this traffic event:
SITUATION_ASSESSMENT: [what's happening]
REROUTING_STRATEGY: [specific route changes]
SIGNALS_TO_ADJUST: [which traffic signals]
ESTIMATED_RESOLUTION: [time to clear]
ALERTS_TO_BROADCAST: [public notifications]
"""

EMERGENCY_REACTION_PROMPT = """
You are an emergency response coordinator.

Emergency event received:
{event}

Coordinate emergency response:
RESPONSE_LEVEL: 1/2/3 (1=highest)
UNITS_TO_DISPATCH: [police/fire/ambulance counts]
IMMEDIATE_ACTIONS: [first 5 minutes]
COORDINATION_NEEDED: [other agencies to contact]
PUBLIC_ADVISORY: [what to tell public]
"""

MAINTENANCE_REACTION_PROMPT = """
You are a city infrastructure maintenance agent.

Infrastructure event received:
{event}

Plan maintenance response:
PRIORITY: immediate/urgent/scheduled
CREW_NEEDED: [type and size of crew]
EQUIPMENT_REQUIRED: [specific equipment]
ESTIMATED_REPAIR_TIME: [duration]
AFFECTED_SERVICES: [what citizens lose]
WORKAROUND: [temporary solution if any]
"""

STREAM_ANALYTICS_PROMPT = """
You are a city analytics agent processing event stream.

Recent events processed:
{events_batch}

Analyze patterns:
HOTSPOT_LOCATIONS: [areas with most events]
PEAK_EVENT_TYPES: [most common events]
CONCERNING_TRENDS: [patterns that need attention]
CITY_STATUS: normal/elevated/critical
RECOMMENDATIONS: [proactive measures]
"""

REPLAY_ANALYSIS_PROMPT = """
You are analyzing historical city events for patterns.

Historical event replay ({count} events):
{historical_events}

Deep pattern analysis:
RECURRING_ISSUES: [problems that repeat]
TIME_PATTERNS: [when events cluster]
LOCATION_CLUSTERS: [geographic problem areas]
ROOT_CAUSES: [likely underlying causes]
PREVENTIVE_MEASURES: [how to prevent future events]
MODEL_UPDATES_NEEDED: [what agent models should learn]
"""
