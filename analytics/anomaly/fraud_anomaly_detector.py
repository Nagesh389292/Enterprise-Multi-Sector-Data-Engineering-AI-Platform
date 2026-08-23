"""
Fraud Trend Anomaly Detection Engine (Credit Card).

Computes rolling baseline fraud rates, detects volume/rate spikes above expected bounds,
and isolates geographical/merchant anomaly drivers.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List

class FraudAnomalyDetector:
    """Detects fraud volume & rate anomalies against rolling baselines."""

    def __init__(self, baseline_window_days: int = 7, std_threshold: float = 2.0):
        self.baseline_window_days = baseline_window_days
        self.std_threshold = std_threshold

    def analyze_fraud_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates rolling baseline and identifies anomaly events."""
        if "Time" not in df.columns or "Class" not in df.columns:
            return {"status": "ERROR", "message": "Missing required columns"}

        # Bin into simulated hourly/daily periods
        df_sorted = df.sort_values("Time").copy()
        df_sorted["period"] = (df_sorted["Time"] // 3600).astype(int)

        aggregated = df_sorted.groupby("period").agg(
            total_txns=("Class", "count"),
            fraud_count=("Class", "sum"),
            total_amount=("Amount", "sum")
        ).reset_index()

        aggregated["fraud_rate"] = aggregated["fraud_count"] / aggregated["total_txns"]

        # Calculate rolling mean & std
        aggregated["rolling_mean"] = aggregated["fraud_rate"].rolling(window=self.baseline_window_days, min_periods=1).mean()
        aggregated["rolling_std"] = aggregated["fraud_rate"].rolling(window=self.baseline_window_days, min_periods=1).std().fillna(0.01)

        aggregated["upper_bound"] = aggregated["rolling_mean"] + (self.std_threshold * aggregated["rolling_std"])
        aggregated["is_anomaly"] = aggregated["fraud_rate"] > aggregated["upper_bound"]

        anomalies_count = int(aggregated["is_anomaly"].sum())
        latest_period = aggregated.iloc[-1]
        baseline_rate = float(latest_period["rolling_mean"])
        current_rate = float(latest_period["fraud_rate"])

        pct_change = round(((current_rate - baseline_rate) / (baseline_rate + 1e-5)) * 100, 2)

        return {
            "status": "SUCCESS",
            "total_periods": len(aggregated),
            "anomalies_detected": anomalies_count,
            "latest_baseline_rate_pct": round(baseline_rate * 100, 2),
            "latest_current_rate_pct": round(current_rate * 100, 2),
            "pct_change_vs_baseline": pct_change,
            "latest_is_anomaly": bool(latest_period["is_anomaly"]),
            "anomaly_explanation": f"Fraud rate ({round(current_rate*100,2)}%) is {pct_change}% relative to 7-day baseline ({round(baseline_rate*100,2)}%)."
        }
