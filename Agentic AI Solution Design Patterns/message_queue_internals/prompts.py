"""
Prompts for message queue internals agents.
"""

ORDER_VALIDATION_PROMPT = """
You are an order processing agent (producer role).

Order to send:
{order}

Validate and prepare for async dispatch:
VALID: yes/no
PRIORITY: 1-4
NOTES: [any special handling]
DECISION: dispatch/hold/reject
"""

FULFILLMENT_PROMPT = """
You are a fulfillment agent (consumer role).

Order received from message queue:
{order}

Process and prepare response:
SHIPPING_METHOD: standard/express/overnight
CARRIER: FedEx/UPS/USPS
ESTIMATED_DAYS: [number]
TRACKING_ID: [generate: carrier-6digits]
STATUS: confirmed/delayed/failed
RESPONSE_NOTES: [message back to order agent]
"""

RESPONSE_PROCESSING_PROMPT = """
You are an order agent receiving fulfillment confirmation.

Correlation ID matched: {correlation_id}
Original order: {original_order}
Fulfillment response: {response}

Process confirmation:
ORDER_STATUS: fulfilled/delayed/failed
CUSTOMER_NOTIFICATION: [what to tell customer]
NEXT_ACTION: [what to do next]
"""
