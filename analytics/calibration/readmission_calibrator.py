"""
Clinical EHR Hospital Readmission Risk Calibration Engine.

Optimizes classification probability thresholds, evaluates Precision-Recall trade-offs,
and stratifies patient hospital readmissions into Low, Medium, and High risk bands.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_recall_curve, auc, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


class ReadmissionCalibrator:
    """Calibrates clinical readmission prediction thresholds and risk bands."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def calibrate_readmission_risk(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calibrates model output probabilities and assigns patient risk tiers."""
        feature_cols = ["TimeInHospitalDays", "NumLabProcedures", "NumMedications", "NumDiagnoses"]
        for col in feature_cols + ["Readmitted30Days"]:
            if col not in df.columns:
                return {"status": "ERROR", "message": f"Missing column {col}"}

        X = df[feature_cols]
        y = df["Readmitted30Days"]

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25, random_state=self.random_state, stratify=y)

        rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=self.random_state)
        rf.fit(X_train, y_train)

        probs = rf.predict_proba(X_val)[:, 1]
        precisions, recalls, thresholds = precision_recall_curve(y_val, probs)
        pr_auc = round(float(auc(recalls, precisions)), 4)

        # Optimize threshold for maximum F1
        f1_scores = [2 * (p * r) / (p + r + 1e-6) for p, r in zip(precisions[:-1], recalls[:-1])]
        best_idx = np.argmax(f1_scores)
        optimal_threshold = round(float(thresholds[best_idx]), 4)
        best_f1 = round(float(f1_scores[best_idx]), 4)

        # Assign risk bands
        df_risk = df.copy()
        all_probs = rf.predict_proba(X)[:, 1]
        df_risk["readmission_prob"] = all_probs

        high_risk_count = int(np.sum(all_probs >= 0.40))
        medium_risk_count = int(np.sum((all_probs >= 0.20) & (all_probs < 0.40)))
        low_risk_count = int(np.sum(all_probs < 0.20))

        return {
            "status": "SUCCESS",
            "total_patients_evaluated": len(df),
            "pr_auc": pr_auc,
            "optimal_decision_threshold": optimal_threshold,
            "optimal_f1_score": best_f1,
            "risk_band_counts": {
                "HIGH_RISK_BAND (>=0.40)": high_risk_count,
                "MEDIUM_RISK_BAND (0.20-0.39)": medium_risk_count,
                "LOW_RISK_BAND (<0.20)": low_risk_count
            },
            "clinical_guidance": f"Optimal decision threshold calibrated to {optimal_threshold} yielding PR-AUC = {pr_auc}. High-risk cohort contains {high_risk_count} patients."
        }
