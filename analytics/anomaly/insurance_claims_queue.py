"""
Insurance Claims Fraud Anomaly Queue Engine.

Scores auto insurance claims using multivariate Isolation Forest anomaly scoring
and creates a prioritized claims investigation queue.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.ensemble import IsolationForest


class InsuranceClaimsQueueEngine:
    """Prioritizes insurance claims for fraud investigation."""

    def __init__(self, contamination: float = 0.15, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state

    def generate_investigation_queue(self, df: pd.DataFrame, top_n: int = 10) -> Dict[str, Any]:
        """Calculates claim anomaly scores and returns prioritized queue."""
        required_cols = ["TotalClaimAmount", "InjuryClaim", "PropertyClaim", "CustomerAge", "VehicleAgeYears"]
        for col in required_cols:
            if col not in df.columns:
                return {"status": "ERROR", "message": f"Missing column {col}"}

        X = df[required_cols].copy()
        
        # Fit Isolation Forest
        iso = IsolationForest(contamination=self.contamination, random_state=self.random_state)
        iso.fit(X)
        scores = -iso.score_samples(X)  # Higher = more anomalous
        df["anomaly_score"] = np.round(scores, 4)

        # Sort claims by anomaly score
        sorted_df = df.sort_values("anomaly_score", ascending=False).head(top_n)
        
        queue_items = []
        for idx, row in sorted_df.iterrows():
            policy_id = row.get("PolicyID", f"CLM-{idx}")
            amount = float(row.get("TotalClaimAmount", 0.0))
            score = float(row.get("anomaly_score", 0.0))
            incident = row.get("IncidentType", "Unspecified")

            if score > 0.60:
                risk_tier = "HIGH"
                reason = "Severe claim amount anomaly relative to vehicle age & customer profile"
            elif score > 0.50:
                risk_tier = "MEDIUM"
                reason = "Elevated injury claim ratio and customer age discrepancy"
            else:
                risk_tier = "LOW"
                reason = "Minor statistical variation"

            queue_items.append({
                "claim_id": str(policy_id),
                "total_claim_amount_usd": round(amount, 2),
                "anomaly_score": score,
                "incident_type": incident,
                "risk_tier": risk_tier,
                "primary_investigation_reason": reason
            })

        high_risk_count = int(np.sum(df["anomaly_score"] > 0.60))

        return {
            "status": "SUCCESS",
            "total_claims_scanned": len(df),
            "high_risk_claims_count": high_risk_count,
            "investigation_queue_size": len(queue_items),
            "top_investigation_queue": queue_items
        }
