"""
PySpark Credit Card End-to-End Medallion Pipeline Orchestrator.
Executes Bronze -> Silver -> Gold PySpark processing, logs benchmark metrics (processing time, rows, partitions, size),
and syncs Gold data into Django PostgreSQL ORM models.
"""

import os
import sys
import json
import time
import random
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List

# Ensure project root & backend package are on Python path
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

def load_env_file():
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env_file()

# Setup Django Environment for DB Syncing
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
try:
    import django
    django.setup()
    from api.models import CreditCardTransaction
    DJANGO_AVAILABLE = True
except Exception:
    DJANGO_AVAILABLE = False

from data_engineering.spark.spark_session import get_spark_session
from data_engineering.spark.bronze import SparkBronzeIngestion
from data_engineering.spark.silver import SparkSilverTransformation
from data_engineering.spark.gold import SparkGoldAggregation

def generate_synthetic_transactions(count: int = 1000) -> List[Dict[str, Any]]:
    """Generates synthetic credit card transaction batch for benchmarking."""
    records = []
    card_types = ["VISA", "MASTERCARD", "AMEX", "DISCOVER"]
    merchants = ["Electronics", "Travel", "Dining", "Retail", "Luxury", "Grocery"]
    locations = ["Mumbai", "Bengaluru", "Delhi", "Hyderabad", "London", "Unknown IP", "New York"]

    now = datetime.now(timezone.utc).isoformat()

    for i in range(count):
        is_fraud = random.random() < 0.08
        amount = round(random.uniform(5000.0, 99000.0) if is_fraud else random.uniform(10.0, 1500.0), 2)
        loc = random.choice(["London", "Unknown IP", "New York"]) if is_fraud else random.choice(locations[:4])
        device = f"DEV-9{random.randint(10,99)}" if is_fraud else f"DEV-{random.randint(100,200)}"

        txn_id = f"TXN-SPARK-{random.randint(100000, 999999)}"
        records.append({
            "transaction_id": txn_id,
            "event_id": txn_id,
            "customer_id": f"CUST-{random.randint(1000, 1500)}",
            "amount": amount,
            "card_type": random.choice(card_types),
            "merchant": random.choice(merchants),
            "location": loc,
            "device_id": device,
            "timestamp": now,
            "is_fraud_ground_truth": int(is_fraud)
        })
    return records


class PySparkCreditCardPipeline:
    """End-to-End PySpark Medallion Orchestrator for Credit Card Data Lake."""
    def __init__(self, app_name: str = "CreditCardMedallionPipeline"):
        self.spark = get_spark_session(app_name)
        self.bronze_engine = SparkBronzeIngestion(self.spark)
        self.silver_engine = SparkSilverTransformation(self.spark)
        self.gold_engine = SparkGoldAggregation(self.spark)

    def run_pipeline(self, raw_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Executes Bronze -> Silver -> Gold pipeline and computes performance benchmark metrics."""
        t_start = time.time()
        
        # 1. Bronze Processing
        bronze_res = self.bronze_engine.process_raw_data(raw_records)
        
        # 2. Silver Processing
        silver_res = self.silver_engine.process_silver_layer()
        
        # 3. Gold Processing
        gold_res = self.gold_engine.process_gold_layer()
        
        t_elapsed = round(time.time() - t_start, 3)

        # Calculate partition count & directory size
        total_parquet_bytes = 0
        partition_count = 0
        lake_root = "data/lake"
        if os.path.exists(lake_root):
            for root, dirs, files in os.walk(lake_root):
                if any(f.endswith(".parquet") for f in files):
                    partition_count += 1
                for f in files:
                    total_parquet_bytes += os.path.getsize(os.path.join(root, f))

        output_size_mb = round(total_parquet_bytes / (1024 * 1024), 2)

        # 4. Sync Gold dataset to Django PostgreSQL DB if available
        db_synced_count = 0
        if DJANGO_AVAILABLE:
            try:
                df_daily = self.spark.read.parquet("data/lake/gold/gold_daily_transactions")
                sample_rows = df_daily.limit(500).collect()
                for row in sample_rows:
                    CreditCardTransaction.objects.get_or_create(
                        event_id=row["transaction_id"],
                        defaults={
                            "customer_id": row["customer_id"],
                            "amount": float(row["amount"]),
                            "merchant": row["merchant"],
                            "location": row["location"],
                            "device_id": row["device_id"],
                            "fraud_probability": 0.95 if row["is_fraud_ground_truth"] == 1 else 0.02,
                            "risk_score": 95 if row["is_fraud_ground_truth"] == 1 else 5,
                            "risk_level": "HIGH" if row["is_fraud_ground_truth"] == 1 else "LOW",
                            "is_fraud_predicted": bool(row["is_fraud_ground_truth"] == 1),
                            "explanation_reasons": ["Spark Medallion Batch Pipeline Ingested"]
                        }
                    )
                db_synced_count = CreditCardTransaction.objects.count()
            except Exception:
                db_synced_count = 0

        pipeline_report = {
            "pipeline": "PySpark Credit Card Medallion Pipeline",
            "spark_version": self.spark.version,
            "status": "SUCCESS",
            "benchmark_metrics": {
                "total_processing_time_sec": t_elapsed,
                "total_raw_input_rows": len(raw_records),
                "bronze_rows_ingested": bronze_res["rows_ingested"],
                "silver_valid_rows": silver_res["silver_valid_rows"],
                "quarantined_failed_rows": silver_res["quarantined_rows"],
                "gold_marts_created": len(gold_res["gold_marts_created"]),
                "partition_count": partition_count,
                "output_parquet_size_mb": output_size_mb,
                "db_total_synced_rows": db_synced_count
            },
            "bronze": bronze_res,
            "silver": silver_res,
            "gold": gold_res
        }
        return pipeline_report

    def close(self):
        if self.spark:
            self.spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PySpark Credit Card Medallion Pipeline Orchestrator")
    parser.add_argument("--sample-count", type=int, default=1000, help="Number of synthetic raw transactions to process")
    args = parser.parse_args()

    print(f"Starting PySpark Medallion Pipeline with {args.sample_count} records...")
    records = generate_synthetic_transactions(count=args.sample_count)
    pipeline = PySparkCreditCardPipeline()
    try:
        report = pipeline.run_pipeline(records)
        print(json.dumps(report, indent=2))
    finally:
        pipeline.close()
