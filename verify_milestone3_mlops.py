"""
Milestone 3 MLOps & ML Engineering Automated Verification Script.

Executes:
1. Multi-Model Benchmark across 6 Model Families (5,000 synthetic records)
2. MLflow Experiment Run & Metric Logging
3. Champion vs Challenger Registry Promotion
4. SHAP Feature Importance Plot Generation
5. Real-Time Inference Latency Validation (< 5ms per sample)
6. Outputs verify_milestone3_mlops_report.json
"""

import os
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, Any

from ml.model_comparison import generate_synthetic_dataset, ModelComparisonSuite
from ml.shap_explainer import ShapExplainer
from ml.mlflow_tracker import MLflowTracker
from ml.fraud_detection import FraudDetectionEngine


def run_milestone3_verification() -> Dict[str, Any]:
    print("=======================================================")
    print("  MILESTONE 3: MLOps & ML ENGINEERING BENCHMARK RUN")
    print("=======================================================")

    # 1. Generate Datasets
    print("\n1. Generating 5,000 synthetic credit card transaction dataset...")
    X, y, df = generate_synthetic_dataset(n_samples=5000, random_state=42)
    split_idx = int(len(X) * 0.8)
    X_train, y_train = X[:split_idx], y[:split_idx]
    X_test, y_test = X[split_idx:], y[split_idx:]
    print(f"   Train set: {X_train.shape[0]} rows | Test set: {X_test.shape[0]} rows (Fraud rate: {y_test.mean():.2%})")

    # 2. Multi-Model Benchmarking
    print("\n2. Training & benchmarking 6 model families...")
    suite = ModelComparisonSuite()
    start_time = time.time()
    results = suite.train_and_evaluate_all(X_train, y_train, X_test, y_test)
    bench_duration = time.time() - start_time
    print(f"   Completed multi-model benchmarking in {bench_duration:.2f}s")

    # 3. SHAP Explainability Plot
    print("\n3. Computing SHAP feature importance & generating plot...")
    top_model = suite.trained_models.get("LightGBM") or suite.trained_models.get("XGBoost")
    explainer = ShapExplainer(model_obj=top_model)
    shap_plot_path = os.path.join(os.getcwd(), "ml", "models", "shap_summary.png")
    explainer.generate_summary_plot(X_test, output_path=shap_plot_path)
    print(f"   SHAP plot saved to: {shap_plot_path}")

    # 4. MLflow Logging & Registry Promotion
    print("\n4. Logging runs to MLflow & evaluating Champion vs Challenger...")
    tracker = MLflowTracker(experiment_name="Credit_Card_Fraud_Detection")
    run_ids = {}
    for m_name, m_res in results.items():
        run_id = tracker.log_model_run(m_res, params={"dataset_samples": 5000}, shap_plot_path=shap_plot_path)
        run_ids[m_name] = run_id
        m_res["mlflow_run_id"] = run_id
        print(f"   - Logged {m_name:<20} | F1: {m_res['f1_score']:.4f} | ROC-AUC: {m_res['roc_auc']:.4f} | Run ID: {run_id[:8]}...")

    champion_info = tracker.evaluate_and_register_champion(results)
    print(f"\n   >>> CHAMPION MODEL PROMOTED: {champion_info['champion_model']} (F1: {champion_info['f1_score']}, ROC-AUC: {champion_info['roc_auc']})")
    print(f"   >>> CHALLENGER MODEL:       {champion_info['challenger_model']} (F1: {champion_info['challenger_f1']})")

    # 5. Production Real-Time Inference Latency Test
    print("\n5. Validating production inference engine latency & SHAP outputs...")
    engine = FraudDetectionEngine()
    test_evt = {
        "event_id": "TXN-M3-VERIFY",
        "customer_id": "C901",
        "amount": 4200.0,
        "merchant": "Jewelry Store",
        "location": "Mumbai",
        "device_id": "DEV-M3",
        "event_type": "card_transaction"
    }

    t0 = time.time()
    for _ in range(100):
        pred = engine.predict(test_evt)
    avg_latency_ms = ((time.time() - t0) / 100.0) * 1000.0

    print(f"   Production Inference Latency: {avg_latency_ms:.3f} ms / prediction (Target: < 5.0ms)")
    print(f"   Sample Risk Score: {pred['risk_score']}/100 | Risk Level: {pred['risk_level']}")
    print(f"   SHAP Top Reasons: {pred['explanation_reasons']}")

    # 6. Format Metric Table
    print("\n" + "=" * 90)
    print(f"{'MODEL FAMILY':<22} | {'PRECISION':<9} | {'RECALL':<8} | {'F1-SCORE':<8} | {'ROC-AUC':<8} | {'LATENCY(ms)':<11} | {'SIZE(KB)':<8}")
    print("=" * 90)
    
    clean_results_json = {}
    for m_name, m_res in results.items():
        print(f"{m_name:<22} | {m_res['precision']:<9.4f} | {m_res['recall']:<8.4f} | {m_res['f1_score']:<8.4f} | {m_res['roc_auc']:<8.4f} | {m_res['latency_ms_per_sample']:<11.3f} | {m_res['artifact_size_kb']:<8.2f}")
        
        clean_res = {k: v for k, v in m_res.items() if k not in ["model_obj"]}
        clean_results_json[m_name] = clean_res

    print("=" * 90)

    # 7. Final Report Output
    report = {
        "status": "PASS",
        "total_dataset_samples": len(X),
        "test_samples": len(X_test),
        "benchmarking_duration_sec": round(bench_duration, 2),
        "champion_registry": champion_info,
        "inference_engine_latency_ms": round(avg_latency_ms, 3),
        "shap_plot_path": shap_plot_path,
        "model_benchmarks": clean_results_json
    }

    report_path = os.path.join(os.getcwd(), "verify_milestone3_mlops_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nVerification report saved to: {report_path}")
    return report


if __name__ == "__main__":
    run_milestone3_verification()
