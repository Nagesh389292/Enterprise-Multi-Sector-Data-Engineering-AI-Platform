"""
Real-Time Event Stream Producer for Credit Card Transactions.
Publishes streaming transactions to Redis stream 'stream:credit_card_events' with fallback queue.
"""

import os
import json
import time
import random
from datetime import datetime, timezone
from typing import Dict, Any, List

def load_env_file():
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env_file()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisStreamProducer:
    """Publishes transaction events to Redis Stream or local fallback bus."""
    def __init__(self):
        self.redis_client = None
        self._init_redis()
        self.local_event_queue: List[Dict[str, Any]] = []

    def _init_redis(self):
        try:
            import redis
            self.redis_client = redis.from_url(REDIS_URL, socket_timeout=2)
            self.redis_client.ping()
        except Exception:
            self.redis_client = None

    def publish_event(self, event: Dict[str, Any]) -> bool:
        """Publishes event to Redis stream 'stream:credit_card_events'."""
        payload_str = json.dumps(event)
        if self.redis_client:
            try:
                self.redis_client.xadd("stream:credit_card_events", {"payload": payload_str})
                return True
            except Exception:
                pass
        
        # Local fallback queue
        self.local_event_queue.append(event)
        return True

    def generate_live_burst(self, count: int = 5, fraud_spike: bool = False) -> List[Dict[str, Any]]:
        """Generates and publishes a live stream event burst."""
        events = []
        card_types = ["VISA", "MASTERCARD", "AMEX", "DISCOVER"]
        for i in range(count):
            is_fraud = fraud_spike or (random.random() < 0.15)
            amount = round(random.uniform(5500.0, 95000.0) if is_fraud else random.uniform(25.0, 850.0), 2)
            location = random.choice(["London", "Unknown IP", "New York"]) if is_fraud else random.choice(["Hyderabad", "Mumbai", "Bengaluru", "Delhi"])
            device_id = f"DEV-{random.randint(900, 999)}" if is_fraud else f"DEV-{random.randint(100, 200)}"

            evt = {
                "event_id": f"TXN-{random.randint(10000, 99999)}",
                "transaction_id": f"TXN-{random.randint(10000, 99999)}",
                "customer_id": f"C{random.randint(1000, 1050)}",
                "amount": amount,
                "card_type": random.choice(card_types),
                "merchant": random.choice(["Electronics", "Travel", "Dining", "Retail"]),
                "location": location,
                "device_id": device_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "card_transaction",
                "is_fraud_ground_truth": int(is_fraud)
            }
            self.publish_event(evt)
            events.append(evt)
        return events

if __name__ == "__main__":
    producer = RedisStreamProducer()
    print("Publishing Live Stream Event Burst:")
    published = producer.generate_live_burst(count=5, fraud_spike=True)
    print(json.dumps(published, indent=2))
