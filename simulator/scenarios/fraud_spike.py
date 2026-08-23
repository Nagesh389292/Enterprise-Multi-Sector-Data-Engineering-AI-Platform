"""
Scenario Simulator: Fraud Spike Incident.
Injects a high-velocity burst of suspicious credit card transactions to demonstrate real-time detection and alerting.
"""

import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

from simulator.credit_card_generator import generate_single_transaction
from data_engineering.validation.validator import get_credit_card_validator
from ml.fraud_detection import FraudDetectionEngine

def run_fraud_spike_scenario(event_count: int = 20) -> Dict[str, Any]:
    validator = get_credit_card_validator()
    fraud_engine = FraudDetectionEngine()

    print(f"[{datetime.now(timezone.utc).isoformat()}] STARTING SCENARIO: Fraud Spike Incident ({event_count} events)...")
    
    events: List[Dict[str, Any]] = []
    alerts: List[Dict[str, Any]] = []
    
    for i in range(1, event_count + 1):
        # 70% chance of fraudulent high-value transaction during spike
        evt = generate_single_transaction(fraud_bias=0.70)
        events.append(evt)
        
        # 1. Validate
        val_res = validator.validate_record(evt)
        if not val_res.is_valid:
            print(f"  [QUARANTINED] Record {evt['transaction_id']} failed validation: {val_res.errors}")
            continue

        # 2. Score with Fraud ML Engine
        ml_res = fraud_engine.predict(evt)
        
        if ml_res["risk_level"] in ["HIGH", "MEDIUM"]:
            alert = {
                "alert_id": f"ALT_{i:03d}",
                "timestamp": evt["timestamp"],
                "transaction_id": evt["transaction_id"],
                "customer_id": evt["customer_id"],
                "amount": evt["amount"],
                "location": evt["location"],
                "fraud_probability": ml_res["fraud_probability"],
                "risk_score": ml_res["risk_score"],
                "risk_level": ml_res["risk_level"]
            }
            alerts.append(alert)
            print(f"  [FRAUD ALERT] {alert['risk_level']} RISK! Txn: {alert['transaction_id']}, Amount: ${alert['amount']}, Score: {alert['risk_score']}/100")

    summary = {
        "scenario": "Fraud Spike Incident",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_events_generated": event_count,
        "total_alerts_triggered": len(alerts),
        "high_risk_alerts": len([a for a in alerts if a["risk_level"] == "HIGH"]),
        "medium_risk_alerts": len([a for a in alerts if a["risk_level"] == "MEDIUM"]),
        "alerts_sample": alerts[:5]
    }
    return summary

if __name__ == "__main__":
    res = run_fraud_spike_scenario(event_count=15)
    print("\nScenario Summary:")
    print(json.dumps(res, indent=2))
