"""
Synthetic Stream Ingestion for Credit Card Transactions.
Produces high-velocity event streams for batch and streaming pipelines.
"""

import random
from datetime import datetime, timezone
from typing import Dict, Any, List

def generate_credit_card_event(fraud_rate: float = 0.05) -> Dict[str, Any]:
    is_fraud = random.random() < fraud_rate
    amount = round(random.uniform(5500.0, 98000.0) if is_fraud else random.uniform(10.0, 3500.0), 2)
    location = random.choice(["London", "New York", "Unknown IP"]) if is_fraud else random.choice(["Mumbai", "Delhi", "Bengaluru", "Hyderabad"])

    return {
        "event_id": f"TXN-{random.randint(10000, 99999)}",
        "customer_id": f"C{random.randint(1000, 1999)}",
        "amount": amount,
        "merchant": random.choice(["Electronics", "Travel", "Dining", "Retail", "Services"]),
        "location": location,
        "device_id": f"DEV-{random.randint(100, 999)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "card_transaction",
        "is_fraud": int(is_fraud)
    }

def generate_event_batch(size: int = 100, fraud_rate: float = 0.05) -> List[Dict[str, Any]]:
    return [generate_credit_card_event(fraud_rate=fraud_rate) for _ in range(size)]
