"""
Production Real-Time Credit Card Fraud Detection Inference Engine.

Wraps model artifacts, feature store transforms, SHAP explainability,
and PyTorch Autoencoder reconstruction anomaly detection for low-latency
real-time inference (< 5.0ms target).
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List

from sklearn.ensemble import IsolationForest
import xgboost as xgb

torch_available = False
try:
    import torch
    import torch.nn as nn
    torch_available = True
except ImportError:
    torch = None
    nn = None

from ml.feature_engineering import feature_store
from ml.shap_explainer import ShapExplainer, FEATURE_NAMES

MODEL_DIR = os.path.join(os.getcwd(), "ml", "models")


if torch_available and nn is not None:
    class PyTorchAutoencoder(nn.Module):
        def __init__(self, input_dim: int = 5):
            super(PyTorchAutoencoder, self).__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, 8),
                nn.ReLU(),
                nn.Linear(8, 4),
                nn.ReLU()
            )
            self.decoder = nn.Sequential(
                nn.Linear(4, 8),
                nn.ReLU(),
                nn.Linear(8, input_dim),
                nn.Sigmoid()
            )

        def forward(self, x):
            return self.decoder(self.encoder(x))
else:
    class PyTorchAutoencoder:
        def __init__(self, input_dim: int = 5):
            pass
        def __call__(self, x):
            return x


class FraudDetectionEngine:
    """Real-time inference engine combining Supervised Classifier + Autoencoder + SHAP."""

    def __init__(self, model_dir: str = MODEL_DIR):
        self.model_dir = model_dir
        self.feature_names = FEATURE_NAMES
        self.model = None
        self.autoencoder = None
        self.shap_explainer = None
        
        self.model_path = os.path.join(self.model_dir, "xgboost.pkl")
        self.autoencoder_path = os.path.join(self.model_dir, "pytorch_autoencoder.pt")
        
        self._load_or_train_models()

    def _load_or_train_models(self):
        """Loads trained XGBoost & PyTorch Autoencoder models from disk or initializes defaults."""
        os.makedirs(self.model_dir, exist_ok=True)
        
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
            except Exception:
                self._train_default_baseline()
        else:
            self._train_default_baseline()

        if os.path.exists(self.autoencoder_path) and torch_available:
            try:
                self.autoencoder = PyTorchAutoencoder(input_dim=5)
                self.autoencoder.load_state_dict(torch.load(self.autoencoder_path, weights_only=True))
                self.autoencoder.eval()
            except Exception:
                self.autoencoder = PyTorchAutoencoder(input_dim=5)
        else:
            self.autoencoder = PyTorchAutoencoder(input_dim=5)

        self.shap_explainer = ShapExplainer(model_obj=self.model, feature_names=self.feature_names)

    def _train_default_baseline(self):
        """Generates initial feature dataset and trains baseline XGBoost model."""
        np.random.seed(42)
        n_samples = 600
        
        amounts = np.random.uniform(10.0, 5000.0, n_samples)
        velocities = np.random.randint(1, 5, n_samples)
        zscores = np.random.normal(0, 1, n_samples)
        locations = np.random.binomial(1, 0.1, n_samples)
        devices = np.random.binomial(1, 0.1, n_samples)

        is_fraud = ((amounts > 3500.0) | (locations == 1) | (velocities > 3)).astype(int)

        X = np.column_stack([amounts, velocities, zscores, locations, devices])
        y = is_fraud

        self.model = xgb.XGBClassifier(n_estimators=50, max_depth=4, learning_rate=0.1, eval_metric="logloss")
        self.model.fit(X, y)

        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)

    def predict(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Runs feature extraction, classification inference, SHAP attribution, and anomaly loss scoring."""
        features = feature_store.extract_features(event)
        
        X_input = np.array([[
            features["amount"],
            features["velocity_5m"],
            features["amount_zscore"],
            features["is_unusual_location"],
            features["is_new_device"]
        ]], dtype=np.float32)

        # 1. Supervised / Unsupervised Fraud Probability
        if self.model is not None and hasattr(self.model, "predict_proba"):
            prob = float(self.model.predict_proba(X_input)[0, 1])
        elif self.model is not None and hasattr(self.model, "decision_function"):
            raw_s = float(self.model.decision_function(X_input)[0])
            if isinstance(self.model, IsolationForest):
                prob = float(np.clip(0.5 - raw_s * 2.0, 0.0, 1.0))
            else:
                prob = float(1.0 / (1.0 + np.exp(-raw_s)))
        else:
            prob = 0.85 if features["amount"] > 4000.0 or features["is_unusual_location"] else 0.05

        # Domain Rule Overrides for extreme amounts / combined anomalies
        if features["amount"] > 10000.0 or (features["amount"] > 3500.0 and (features["is_unusual_location"] or features["is_new_device"])):
            prob = max(prob, 0.95)

        # 2. PyTorch Autoencoder Reconstruction Anomaly Score
        reconstruction_loss = 0.0
        if torch_available and hasattr(self.autoencoder, "eval"):
            try:
                with torch.no_grad():
                    tensor_in = torch.tensor(X_input, dtype=torch.float32)
                    tensor_out = self.autoencoder(tensor_in)
                    reconstruction_loss = float(torch.mean((tensor_in - tensor_out) ** 2).item())
            except Exception:
                reconstruction_loss = 0.05

        # 3. SHAP Feature Attribution & Explanation Layer
        shap_info = self.shap_explainer.explain_sample(X_input) if self.shap_explainer else {}
        reasons = shap_info.get("top_reasons", [])

        # Heuristic fallback if SHAP produces generic reasons for high risk
        risk_score = int(min(100, max(0, prob * 100)))
        if features["amount"] > 3500.0 and "Unusual high transaction amount" not in " ".join(reasons):
            reasons.append("Unusual high transaction amount")
        if features["is_unusual_location"] and "geographic location" not in " ".join(reasons):
            reasons.append("Unusual geographic location / IP anomaly")

        return {
            "event_id": event.get("event_id"),
            "customer_id": event.get("customer_id"),
            "amount": features["amount"],
            "location": features["location"],
            "device_id": features["device_id"],
            "fraud_probability": round(prob, 4),
            "anomaly_reconstruction_loss": round(reconstruction_loss, 4),
            "risk_score": risk_score,
            "risk_level": "HIGH" if risk_score >= 70 else ("MEDIUM" if risk_score >= 30 else "LOW"),
            "is_fraud_predicted": int(risk_score >= 70),
            "explanation_reasons": reasons,
            "shap_values": shap_info.get("shap_values", {}),
            "engineered_features": features
        }


if __name__ == "__main__":
    engine = FraudDetectionEngine()
    test_evt = {
        "event_id": "TXN-84500",
        "customer_id": "C1029",
        "amount": 84500.0,
        "merchant": "Electronics",
        "location": "Hyderabad",
        "device_id": "DEV-921",
        "event_type": "card_transaction"
    }
    print(json.dumps(engine.predict(test_evt), indent=2))
