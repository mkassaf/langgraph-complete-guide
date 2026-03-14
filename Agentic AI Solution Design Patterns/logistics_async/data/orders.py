"""
Sample customer orders for logistics demo.
"""

CUSTOMER_ORDERS = [
    {
        "order_id": "ORD-2847",
        "customer": "Acme Corp",
        "pickup": "Warehouse District A",
        "delivery": "Downtown Office Tower",
        "items": "15 boxes office supplies",
        "weight_kg": 120,
        "time_window": "09:00-12:00",
        "priority": "express",
    },
    {
        "order_id": "ORD-2848",
        "customer": "TechStart Inc",
        "pickup": "Warehouse District B",
        "delivery": "Tech Park Campus",
        "items": "3 server units",
        "weight_kg": 450,
        "time_window": "14:00-17:00",
        "priority": "standard",
    },
    {
        "order_id": "ORD-2849",
        "customer": "MediCare Hospital",
        "pickup": "Medical Supplies Hub",
        "delivery": "City Hospital",
        "items": "Medical equipment",
        "weight_kg": 85,
        "time_window": "08:00-10:00",
        "priority": "critical",
    },
]
