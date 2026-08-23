"""
Real-Time Feature Engineering Engine for Credit Card Streaming Events.
Computes streaming velocity, geographic anomalies, amount z-scores, and device novelty.
"""

import time
import math
from typing import Dict, Any, List
from collections import defaultdict

class RealTimeFeatureStore:
    """In-memory & Redis-compatible sliding window feature store."""
    def __init__(self):
        # Sliding window history per customer: customer_id -> list of (timestamp_seconds, amount, location, device_id)
        self.customer_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def extract_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        customer_id = event.get("customer_id", "CUST_UNKNOWN")
        amount = float(event.get("amount", 0.0))
        location = str(event.get("location", "Unknown"))
        device_id = str(event.get("device_id", "DEV_UNKNOWN"))
        now = time.time()

        # Update customer history (keep last 60 mins)
        history = self.customer_history[customer_id]
        history.append({
            "timestamp": now,
            "amount": amount,
            "location": location,
            "device_id": device_id
        })
        
        # Prune records older than 1 hour (3600s)
        history = [h for h in history if now - h["timestamp"] <= 3600]
        self.customer_history[customer_id] = history

        # Feature 1: Velocity in last 5 minutes (300s)
        window_5m = [h for h in history if now - h["timestamp"] <= 300]
        velocity_5m = len(window_5m)

        # Feature 2: Amount Z-score
        amounts = [h["amount"] for h in history]
        if len(amounts) > 1:
            mean_amt = sum(amounts) / len(amounts)
            variance = sum((x - mean_amt) ** 2 for x in amounts) / len(amounts)
            std_amt = math.sqrt(variance) if variance > 0 else 1.0
            amount_zscore = round((amount - mean_amt) / std_amt, 2)
        else:
            amount_zscore = 0.0

        # Feature 3: Geographic Anomaly
        known_locations = set(h["location"] for h in history[:-1])
        is_unusual_location = int(location in ["London", "Unknown IP", "Overseas"] or (len(known_locations) > 0 and location not in known_locations))

        # Feature 4: Device Novelty
        known_devices = set(h["device_id"] for h in history[:-1])
        is_new_device = int(len(known_devices) > 0 and device_id not in known_devices)

        # Feature 5: High Velocity Risk Trigger (>3 txns in 5 min window)
        is_high_velocity = int(velocity_5m > 3)

        return {
            "event_id": event.get("event_id"),
            "customer_id": customer_id,
            "amount": amount,
            "location": location,
            "device_id": device_id,
            "velocity_5m": velocity_5m,
            "amount_zscore": amount_zscore,
            "is_unusual_location": is_unusual_location,
            "is_new_device": is_new_device,
            "is_high_velocity": is_high_velocity
        }

# Global singleton feature store instance
feature_store = RealTimeFeatureStore()
