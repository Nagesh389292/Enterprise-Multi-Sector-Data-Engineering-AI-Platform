"""
Unit tests for Milestone 3: ML Engineering & MLOps Infrastructure.
"""

import os
import unittest
import numpy as np
import pandas as pd

from ml.model_comparison import (
    generate_synthetic_dataset,
    ModelComparisonSuite,
    FEATURE_NAMES
)
from ml.shap_explainer import ShapExplainer
from ml.mlflow_tracker import MLflowTracker
from ml.fraud_detection import FraudDetectionEngine


class TestMLEngineering(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.X_tr, cls.y_tr, cls.df = generate_synthetic_dataset(n_samples=500, random_state=42)
        cls.X_te, cls.y_te, _ = generate_synthetic_dataset(n_samples=200, random_state=123)

    def test_synthetic_dataset_generation(self):
        """Verifies synthetic dataset creation shape and features."""
        self.assertEqual(self.X_tr.shape, (500, 5))
        self.assertEqual(len(self.y_tr), 500)
        self.assertIn("amount", self.df.columns)
        self.assertIn("label", self.df.columns)

    def test_multi_model_comparison_suite(self):
        """Verifies multi-model benchmarking executes across all 6 model types."""
        suite = ModelComparisonSuite()
        results = suite.train_and_evaluate_all(self.X_tr, self.y_tr, self.X_te, self.y_te)

        expected_models = [
            "Logistic Regression",
            "Random Forest",
            "XGBoost",
            "LightGBM",
            "Isolation Forest",
            "PyTorch Autoencoder"
        ]

        for m_name in expected_models:
            self.assertIn(m_name, results)
            m_data = results[m_name]
            self.assertGreaterEqual(m_data["f1_score"], 0.0)
            self.assertLessEqual(m_data["f1_score"], 1.0)
            self.assertGreaterEqual(m_data["roc_auc"], 0.0)
            self.assertLessEqual(m_data["roc_auc"], 1.0)
            self.assertIn("tp", m_data["confusion_matrix"])
            self.assertGreater(m_data["latency_ms_per_sample"], 0.0)

    def test_shap_explainer(self):
        """Verifies SHAP value generation and summary plot creation."""
        suite = ModelComparisonSuite()
        suite.train_and_evaluate_all(self.X_tr[:200], self.y_tr[:200], self.X_te[:50], self.y_te[:50])
        xgb_model = suite.trained_models["XGBoost"]

        explainer = ShapExplainer(model_obj=xgb_model, feature_names=FEATURE_NAMES)
        sample = self.X_te[0:1]
        shap_res = explainer.explain_sample(sample)

        self.assertIn("shap_values", shap_res)
        self.assertIn("top_reasons", shap_res)
        self.assertEqual(len(shap_res["shap_values"]), 5)

        plot_path = os.path.join(os.getcwd(), "ml", "models", "test_shap_summary.png")
        saved_plot = explainer.generate_summary_plot(self.X_te[:20], output_path=plot_path)
        self.assertTrue(os.path.exists(saved_plot))

    def test_mlflow_tracker_and_champion_registry(self):
        """Verifies MLflow experiment tracking and Champion model promotion."""
        suite = ModelComparisonSuite()
        bench_results = suite.train_and_evaluate_all(self.X_tr[:200], self.y_tr[:200], self.X_te[:50], self.y_te[:50])

        tracker = MLflowTracker(experiment_name="Test_Fraud_Detection")
        for m_name, m_res in bench_results.items():
            run_id = tracker.log_model_run(m_res, params={"n_samples": 200})
            self.assertIsNotNone(run_id)

        champ_info = tracker.evaluate_and_register_champion(bench_results)
        self.assertIn("champion_model", champ_info)
        self.assertEqual(champ_info["status"], "CHAMPION_PROMOTED")

        reg_info = tracker.get_registered_champion()
        self.assertIsNotNone(reg_info)
        self.assertEqual(reg_info["champion_model"], champ_info["champion_model"])

    def test_fraud_detection_engine_inference(self):
        """Verifies FraudDetectionEngine returns predictions with SHAP attributions."""
        engine = FraudDetectionEngine()
        test_event = {
            "event_id": "TXN-TEST-99",
            "customer_id": "C999",
            "amount": 7500.0,
            "merchant": "Luxury Store",
            "location": "New York",
            "device_id": "DEV-UNKNOWN",
            "event_type": "card_transaction"
        }
        res = engine.predict(test_event)

        self.assertEqual(res["event_id"], "TXN-TEST-99")
        self.assertGreaterEqual(res["fraud_probability"], 0.0)
        self.assertLessEqual(res["fraud_probability"], 1.0)
        self.assertIn("risk_level", res)
        self.assertIn("explanation_reasons", res)
        self.assertIn("shap_values", res)


if __name__ == "__main__":
    unittest.main()
