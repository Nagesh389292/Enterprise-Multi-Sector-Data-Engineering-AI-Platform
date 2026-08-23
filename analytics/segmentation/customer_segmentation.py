"""
Customer Credit Risk Segmentation Engine (Banking).

Applies K-Means clustering, PCA dimensionality reduction, and risk profiling
to segment banking loan applicants into Low, Moderate, and High Risk cohorts.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


class CustomerSegmentationEngine:
    """Segments bank customers into credit risk clusters."""

    def __init__(self, n_clusters: int = 3, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state

    def segment_customers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Clusters loan applicants based on financial features."""
        required_cols = ["Age", "AnnualIncome", "CreditAmount", "DurationMonths"]
        for col in required_cols:
            if col not in df.columns:
                return {"status": "ERROR", "message": f"Missing column {col}"}

        X = df[required_cols].copy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Fit K-Means
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        df["cluster"] = clusters

        # Fit PCA for 2D visualization coordinate mapping
        pca = PCA(n_components=2, random_state=self.random_state)
        pca_coords = pca.fit_transform(X_scaled)
        df["pca_x"] = pca_coords[:, 0]
        df["pca_y"] = pca_coords[:, 1]

        # Profile clusters & assign risk labels based on DefaultRisk if present
        cluster_profiles = []
        for c in range(self.n_clusters):
            sub = df[df["cluster"] == c]
            avg_income = float(sub["AnnualIncome"].mean())
            avg_credit = float(sub["CreditAmount"].mean())
            avg_duration = float(sub["DurationMonths"].mean())
            default_rate = float(sub["DefaultRisk"].mean() * 100) if "DefaultRisk" in sub.columns else 0.0

            if default_rate > 50.0:
                risk_label = "HIGH_RISK"
            elif default_rate > 25.0:
                risk_label = "MODERATE_RISK"
            else:
                risk_label = "LOW_RISK"

            cluster_profiles.append({
                "cluster_id": c,
                "customer_count": len(sub),
                "risk_label": risk_label,
                "avg_annual_income_usd": round(avg_income, 2),
                "avg_credit_amount_usd": round(avg_credit, 2),
                "avg_duration_months": round(avg_duration, 1),
                "default_rate_pct": round(default_rate, 2)
            })

        return {
            "status": "SUCCESS",
            "total_customers_segmented": len(df),
            "n_clusters": self.n_clusters,
            "pca_explained_variance_ratio": [round(float(v), 4) for v in pca.explained_variance_ratio_],
            "cluster_profiles": cluster_profiles
        }
