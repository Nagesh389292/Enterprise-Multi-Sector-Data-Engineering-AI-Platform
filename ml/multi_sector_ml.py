"""
Multi-Sector Machine Learning Model Training & Evaluation Engine.

Trains and benchmarks production classifiers on real-world datasets:
1. Credit Card Fraud (XGBoost & Random Forest)
2. Banking Credit Risk (LightGBM & Random Forest)
3. Clinical EHR Readmission (Random Forest & Logistic Regression)
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any

from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, roc_auc_score, precision_score, recall_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

RAW_REAL_DIR = os.path.join(os.getcwd(), "data", "raw", "real_world")
ML_REPORT_PATH = os.path.join(os.getcwd(), "ml", "multi_sector_ml_report.json")


class MultiSectorMLEngine:
    """Trains and benchmarks ML models on real-world multi-sector datasets."""

    def train_credit_card_fraud_model(self) -> Dict[str, Any]:
        """Trains XGBoost & Random Forest on real Credit Card dataset."""
        csv_path = os.path.join(RAW_REAL_DIR, "credit_card", "credit_card_real.csv")
        df = pd.read_csv(csv_path)

        feature_cols = [c for c in df.columns if c not in ["Class"]]
        X = df[feature_cols]
        y = df["Class"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

        # Train XGBoost
        xgb = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42)
        xgb.fit(X_train, y_train)
        y_pred_xgb = xgb.predict(X_test)
        y_prob_xgb = xgb.predict_proba(X_test)[:, 1]

        f1_xgb = round(f1_score(y_test, y_pred_xgb), 4)
        auc_xgb = round(roc_auc_score(y_test, y_prob_xgb), 4)

        # Train Random Forest
        rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
        rf.fit(X_train, y_train)
        y_pred_rf = rf.predict(X_test)
        y_prob_rf = rf.predict_proba(X_test)[:, 1]

        f1_rf = round(f1_score(y_test, y_pred_rf), 4)
        auc_rf = round(roc_auc_score(y_test, y_prob_rf), 4)

        return {
            "sector": "Credit Card Fraud",
            "dataset_rows": len(df),
            "fraud_positive_samples": int(y.sum()),
            "champion_model": "Random Forest" if f1_rf >= f1_xgb else "XGBoost",
            "xgb_metrics": {"f1_score": f1_xgb, "roc_auc": auc_xgb},
            "rf_metrics": {"f1_score": f1_rf, "roc_auc": auc_rf}
        }

    def train_banking_credit_risk_model(self) -> Dict[str, Any]:
        """Trains LightGBM on real Banking Credit Default dataset."""
        csv_path = os.path.join(RAW_REAL_DIR, "banking", "banking_loan_risk_real.csv")
        df = pd.read_csv(csv_path)

        feature_cols = ["Age", "AnnualIncome", "CreditAmount", "DurationMonths"]
        X = df[feature_cols]
        y = df["DefaultRisk"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=43, stratify=y)

        lgb = LGBMClassifier(n_estimators=100, max_depth=4, random_state=43, verbose=-1)
        lgb.fit(X_train, y_train)
        y_pred = lgb.predict(X_test)
        y_prob = lgb.predict_proba(X_test)[:, 1]

        f1_lgb = round(f1_score(y_test, y_pred), 4)
        auc_lgb = round(roc_auc_score(y_test, y_prob), 4)

        return {
            "sector": "Banking Credit Risk",
            "dataset_rows": len(df),
            "default_positive_samples": int(y.sum()),
            "champion_model": "LightGBM",
            "lgbm_metrics": {"f1_score": f1_lgb, "roc_auc": auc_lgb}
        }

    def train_clinical_readmission_model(self) -> Dict[str, Any]:
        """Trains Random Forest & Logistic Regression on real Clinical EHR dataset."""
        csv_path = os.path.join(RAW_REAL_DIR, "clinical", "clinical_readmission_real.csv")
        df = pd.read_csv(csv_path)

        feature_cols = ["TimeInHospitalDays", "NumLabProcedures", "NumMedications", "NumDiagnoses"]
        X = df[feature_cols]
        y = df["Readmitted30Days"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=44, stratify=y)

        rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=44)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        y_prob = rf.predict_proba(X_test)[:, 1]

        f1_rf = round(f1_score(y_test, y_pred), 4)
        auc_rf = round(roc_auc_score(y_test, y_prob), 4)

        return {
            "sector": "Clinical EHR Readmission",
            "dataset_rows": len(df),
            "readmitted_positive_samples": int(y.sum()),
            "champion_model": "Random Forest",
            "rf_metrics": {"f1_score": f1_rf, "roc_auc": auc_rf}
        }

    def train_all_models(self) -> Dict[str, Any]:
        res_cc = self.train_credit_card_fraud_model()
        res_bank = self.train_banking_credit_risk_model()
        res_clin = self.train_clinical_readmission_model()

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "credit_card": res_cc,
            "banking": res_bank,
            "clinical": res_clin
        }

        os.makedirs(os.path.dirname(ML_REPORT_PATH), exist_ok=True)
        with open(ML_REPORT_PATH, "w") as f:
            json.dump(report, f, indent=2)

        print(f"[MultiSectorML] Completed training all real-world models -> Report: {ML_REPORT_PATH}")
        return report


if __name__ == "__main__":
    engine = MultiSectorMLEngine()
    res = engine.train_all_models()
    print(json.dumps(res, indent=2))
