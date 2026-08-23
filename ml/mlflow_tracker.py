"""
MLflow MLOps Experiment Tracking & Champion / Challenger Model Registry.

Manages:
- MLflow Experiment Initialization ("Credit_Card_Fraud_Detection")
- Automated Parameter & Metric Logging (Precision, Recall, F1, ROC-AUC, Latency, Size)
- Model Artifact & SHAP Plot Persistence
- Champion vs Challenger Evaluation & Registry Promotion
"""

import os
import json
import shutil
from typing import Dict, Any, List, Optional

os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
import mlflow

EXPERIMENT_NAME = "Credit_Card_Fraud_Detection"
DB_PATH = os.path.join(os.getcwd(), "mlflow.db")
REGISTRY_META_PATH = os.path.join(os.getcwd(), "ml", "models", "champion_registry.json")


class MLflowTracker:
    """Manages MLflow experiment tracking and local model registry."""

    def __init__(self, experiment_name: str = EXPERIMENT_NAME):
        self.experiment_name = experiment_name
        os.makedirs(os.path.dirname(REGISTRY_META_PATH), exist_ok=True)
        
        # Configure SQLite tracking URI for MLflow 3.x compatibility
        sqlite_uri = f"sqlite:///{DB_PATH.replace('\\', '/')}"
        mlflow.set_tracking_uri(sqlite_uri)

        try:
            self.experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if self.experiment is None:
                self.exp_id = mlflow.create_experiment(self.experiment_name)
            else:
                self.exp_id = self.experiment.experiment_id
            mlflow.set_experiment(self.experiment_name)
        except Exception:
            self.exp_id = "0"

    def log_model_run(self, model_metrics: Dict[str, Any], params: Optional[Dict[str, Any]] = None, shap_plot_path: Optional[str] = None) -> str:
        """Logs a single model evaluation run to MLflow."""
        model_name = model_metrics["model_name"]
        params = params or {}

        with mlflow.start_run(experiment_id=self.exp_id, run_name=model_name) as run:
            run_id = run.info.run_id

            # Log Hyperparameters
            mlflow.log_param("model_name", model_name)
            for p_k, p_v in params.items():
                mlflow.log_param(str(p_k), str(p_v))

            # Log Quantitative Metrics
            mlflow.log_metric("precision", float(model_metrics.get("precision", 0.0)))
            mlflow.log_metric("recall", float(model_metrics.get("recall", 0.0)))
            mlflow.log_metric("f1_score", float(model_metrics.get("f1_score", 0.0)))
            mlflow.log_metric("roc_auc", float(model_metrics.get("roc_auc", 0.0)))
            mlflow.log_metric("pr_auc", float(model_metrics.get("pr_auc", 0.0)))
            mlflow.log_metric("latency_ms_per_sample", float(model_metrics.get("latency_ms_per_sample", 0.0)))
            mlflow.log_metric("artifact_size_kb", float(model_metrics.get("artifact_size_kb", 0.0)))

            # Log Artifacts
            artifact_path = model_metrics.get("artifact_path")
            if artifact_path and os.path.exists(artifact_path):
                mlflow.log_artifact(artifact_path, artifact_path="model")

            if shap_plot_path and os.path.exists(shap_plot_path):
                mlflow.log_artifact(shap_plot_path, artifact_path="plots")

            return run_id

    def evaluate_and_register_champion(self, benchmark_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates all benchmarked models and promotes the Champion (highest F1 & ROC-AUC)."""
        sorted_models = sorted(
            benchmark_results.values(),
            key=lambda m: (m["f1_score"], m["roc_auc"], -m["latency_ms_per_sample"]),
            reverse=True
        )

        champion_metrics = sorted_models[0]
        challenger_metrics = sorted_models[1] if len(sorted_models) > 1 else None

        champion_info = {
            "champion_model": champion_metrics["model_name"],
            "f1_score": champion_metrics["f1_score"],
            "roc_auc": champion_metrics["roc_auc"],
            "precision": champion_metrics["precision"],
            "recall": champion_metrics["recall"],
            "latency_ms": champion_metrics["latency_ms_per_sample"],
            "artifact_path": champion_metrics["artifact_path"],
            "challenger_model": challenger_metrics["model_name"] if challenger_metrics else "None",
            "challenger_f1": challenger_metrics["f1_score"] if challenger_metrics else 0.0,
            "status": "CHAMPION_PROMOTED"
        }

        champion_target = os.path.join(os.getcwd(), "ml", "models", "champion_model.pkl")
        if os.path.exists(champion_metrics["artifact_path"]):
            shutil.copy(champion_metrics["artifact_path"], champion_target)

        with open(REGISTRY_META_PATH, "w") as f:
            json.dump(champion_info, f, indent=2)

        return champion_info

    def get_registered_champion(self) -> Optional[Dict[str, Any]]:
        """Retrieves active Champion model metadata from registry."""
        if os.path.exists(REGISTRY_META_PATH):
            with open(REGISTRY_META_PATH, "r") as f:
                return json.load(f)
        return None
