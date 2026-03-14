"""
Prompts for logistics async agents.
"""

NEW_ORDER_PROMPT = """
You are a new order processing agent in a logistics system.

Incoming customer order:
{order}

Validate and prepare for async dispatch:
ORDER_VALID: yes/no
PRIORITY_LEVEL: critical/express/standard
SPECIAL_REQUIREMENTS: [any special handling]
CORRELATION_ID: {correlation_id}
ACTION: dispatch_to_queue
MESSAGE: [brief confirmation to log]
"""

ROUTE_OPTIMIZATION_PROMPT = """
You are a route optimization agent.

Order received:
{order}

Traffic conditions:
{traffic}

Calculate optimal route:
PICKUP_LOCATION: {pickup}
DELIVERY_LOCATION: {delivery}
TIME_WINDOW: {time_window}
CARGO_WEIGHT: {weight_kg}kg

Provide:
RECOMMENDED_ROUTE: [step by step route]
ESTIMATED_DURATION: [hours:minutes]
DISTANCE_KM: [estimated]
TRAFFIC_AVOIDANCE: [what traffic you're avoiding]
ROUTE_NOTES: [any special routing notes]
CONFIDENCE: [0.0 to 1.0]
"""

VEHICLE_ASSIGNMENT_PROMPT = """
You are a vehicle assignment agent.

Optimized route details:
{route}

Order requirements:
{order}

Available trucks:
{trucks}

Available drivers:
{drivers}

Select best truck and driver:
SELECTED_TRUCK: [truck_id]
TRUCK_REASON: [why this truck]
SELECTED_DRIVER: [driver_id]
DRIVER_REASON: [why this driver]
ASSIGNMENT_CONFIDENCE: [0.0 to 1.0]
ESTIMATED_DEPARTURE: [time]
POTENTIAL_ISSUES: [any concerns or "none"]
"""

DISPATCH_PROMPT = """
You are a dispatch agent sending a truck on a delivery.

Assignment details:
{assignment}

Route plan:
{route}

Order details:
{order}

Prepare dispatch instructions:

TRUCK_GPS_INSTRUCTIONS:
[Turn by turn directions]

DRIVER_SMS:
[Brief SMS message for driver - max 160 chars]

ONBOARD_SYSTEM_DATA:
{pickup address, delivery address, contact, notes}

DISPATCH_STATUS: dispatched
ESTIMATED_DELIVERY: [time]
TRACKING_NUMBER: [generate: TRK-6digits]
"""
