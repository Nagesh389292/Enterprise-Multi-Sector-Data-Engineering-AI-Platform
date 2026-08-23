"""
Credit Card Transaction Event Simulator.
Generates individual real-time transaction event objects for streaming ingestion.
"""

import random
from datetime import datetime, timezone
from typing import Dict, Any

CARD_TYPES = ["VISA", "MASTERCARD", "AMEX", "DISCOVER", "RUPAY"]
MERCHANTS = ["RETAIL", "TRAVEL", "DINING", "ENTERTAINMENT", "SERVICES"]
LOCATIONS = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "London", "New York"]

def generate_single_transaction(fraud_bias: float = 0.05, customer_id: str = None) -> Dict[str, Any]:
    txn_id = f"TXN_{random.randint(100000, 999999)}"
    cust_id = customer_id or f"CUST_{random.randint(1000, 1999)}"
    is_fraud = random.random() < fraud_bias

    if is_fraud:
        amount = round(random.uniform(4500.0, 95000.0), 2)
        location = random.choice(["London", "New York", "Unknown IP"])
    else:
        amount = round(random.uniform(10.0, 2500.0), 2)
        location = random.choice(["Mumbai", "Delhi", "Bengaluru", "Hyderabad"])

    return {
        "transaction_id": txn_id,
        "customer_id": cust_id,
        "amount": amount,
        "card_type": random.choice(CARD_TYPES),
        "merchant_category": random.choice(MERCHANTS),
        "location": location,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_fraud": int(is_fraud)
    }
