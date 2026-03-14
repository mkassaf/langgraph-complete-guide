"""
Prompts for async messaging order processing agents.
"""

ORDER_VALIDATION_PROMPT = """
You are an order processing agent.

Incoming order:
{order}

Validate and categorize:
VALID: yes/no
PRIORITY_LEVEL: 1-4 (1=low, 4=critical)
ROUTING: [which queue to send to]
NOTES: [any special handling needed]
ACTION: send_to_queue / reject / hold
"""

INVENTORY_CHECK_PROMPT = """
You are an inventory management agent.

Order received from queue:
{order}

Current stock levels:
{stock}

Decide:
AVAILABILITY: in_stock/partial/out_of_stock
ALLOCATE: yes/no
STOCK_UPDATE: {{item: new_quantity}}
NEXT_ACTION: forward_to_payment / back_order / cancel
INTERNAL_MESSAGE: [message to send via internal broker]
"""

PAYMENT_PROCESSING_PROMPT = """
You are a payment processing agent.

Order for payment:
{order}

Process payment:
AUTH_REQUEST_ID: [correlation id to use]
AMOUNT: {total}
METHOD: credit_card/debit/wallet
RISK_LEVEL: low/medium/high
DECISION: approve/decline/review
ASYNC_RESPONSE: will_send_correlated_response
"""

FULFILLMENT_PROMPT = """
You are a fulfillment agent processing orders in sequence.

Order #{sequence_number} in queue:
{order}
Payment status: {payment_status}

Determine fulfillment:
SHIPPING_METHOD: standard/express/overnight
CARRIER: FedEx/UPS/USPS
ESTIMATED_DAYS: [number]
TRACKING_ID: [generate realistic tracking number]
WAREHOUSE_INSTRUCTIONS: [picking instructions]
"""
