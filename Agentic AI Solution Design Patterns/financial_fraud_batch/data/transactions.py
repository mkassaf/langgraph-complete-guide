"""
Sample transaction data from various sources.
"""

TRANSACTION_SOURCES = ["online_banking", "credit_card", "atm", "wire_transfer"]

SAMPLE_TRANSACTIONS = [
    {"txn_id": "TXN-001", "customer_id": "CUST-101", "source": "online_banking", "amount": 45.00, "currency": "USD", "merchant": "Amazon", "country": "US"},
    {"txn_id": "TXN-002", "customer_id": "CUST-102", "source": "credit_card", "amount": 1200.00, "currency": "USD", "merchant": "Electronics Store", "country": "US"},
    {"txn_id": "TXN-003", "customer_id": "CUST-101", "source": "atm", "amount": 500.00, "currency": "USD", "merchant": "ATM-NYC-001", "country": "US"},
    {"txn_id": "TXN-004", "customer_id": "CUST-103", "source": "wire_transfer", "amount": 25000.00, "currency": "USD", "merchant": "International Wire", "country": "NG"},
    {"txn_id": "TXN-005", "customer_id": "CUST-102", "source": "online_banking", "amount": 3.50, "currency": "USD", "merchant": "Coffee Shop", "country": "US"},
    {"txn_id": "TXN-006", "customer_id": "CUST-104", "source": "credit_card", "amount": 8900.00, "currency": "USD", "merchant": "Luxury Retail", "country": "FR"},
    {"txn_id": "TXN-007", "customer_id": "CUST-101", "source": "online_banking", "amount": 89.99, "currency": "USD", "merchant": "Streaming Service", "country": "US"},
    {"txn_id": "TXN-008", "customer_id": "CUST-105", "source": "wire_transfer", "amount": 150000.00, "currency": "USD", "merchant": "Real Estate", "country": "US"},
    {"txn_id": "TXN-009", "customer_id": "CUST-102", "source": "atm", "amount": 200.00, "currency": "USD", "merchant": "ATM-LA-042", "country": "US"},
    {"txn_id": "TXN-010", "customer_id": "CUST-103", "source": "credit_card", "amount": 450.00, "currency": "USD", "merchant": "Travel Agency", "country": "US"},
    {"txn_id": "TXN-011", "customer_id": "CUST-101", "source": "credit_card", "amount": 12.00, "currency": "USD", "merchant": "Gas Station", "country": "US"},
    {"txn_id": "TXN-012", "customer_id": "CUST-104", "source": "online_banking", "amount": 7500.00, "currency": "USD", "merchant": "Jewelry Store", "country": "CH"},
]

CUSTOMER_PROFILES = {
    "CUST-101": {"avg_txn": 85, "typical_countries": ["US"], "risk_tier": "low"},
    "CUST-102": {"avg_txn": 250, "typical_countries": ["US"], "risk_tier": "low"},
    "CUST-103": {"avg_txn": 5000, "typical_countries": ["US", "NG"], "risk_tier": "medium"},
    "CUST-104": {"avg_txn": 3000, "typical_countries": ["US", "FR", "CH"], "risk_tier": "high"},
    "CUST-105": {"avg_txn": 50000, "typical_countries": ["US"], "risk_tier": "high"},
}
