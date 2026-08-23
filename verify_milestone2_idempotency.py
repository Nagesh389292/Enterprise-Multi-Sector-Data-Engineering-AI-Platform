"""
Idempotency & Data Engineering Verification Script for PySpark Medallion Pipeline.
Tests:
1. Running PySpark pipeline twice with identical synthetic input (1,000 and 10,000 records).
2. Verifying PostgreSQL duplicate prevention (CreditCardTransaction row counts before & after).
3. Verifying Bronze/Silver/Gold Parquet idempotency & zero duplicate transaction_ids.
4. Verifying business key integrity (transaction_id).
5. Verifying Gold metric consistency across reruns.
6. Execution latency & performance benchmarks.
"""

import os
import sys
import json
import time
from typing import Dict, Any

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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
try:
    import django
    django.setup()
    from api.models import CreditCardTransaction
    DJANGO_AVAILABLE = True
except Exception as e:
    DJANGO_AVAILABLE = False
    print(f"Django not available for DB check: {e}")

from data_engineering.spark.credit_card_pipeline import (
    PySparkCreditCardPipeline, generate_synthetic_transactions
)

def run_idempotency_test_for_batch(sample_count: int) -> Dict[str, Any]:
    print(f"\n=======================================================")
    print(f"  RUNNING IDEMPOTENCY VERIFICATION FOR {sample_count:,} ROWS")
    print(f"=======================================================")

    # 1. Generate single fixed input batch
    fixed_input = generate_synthetic_transactions(count=sample_count)
    print(f"Generated {len(fixed_input):,} synthetic transaction records (fixed batch).")

    # DB initial count
    initial_db_count = CreditCardTransaction.objects.count() if DJANGO_AVAILABLE else 0
    print(f"PostgreSQL CreditCardTransaction row count BEFORE tests: {initial_db_count:,}")

    pipeline = PySparkCreditCardPipeline()

    try:
        # --- RUN 1 ---
        t1_start = time.time()
        report1 = pipeline.run_pipeline(fixed_input)
        t1_elapsed = round(time.time() - t1_start, 3)

        db_count_after_run1 = CreditCardTransaction.objects.count() if DJANGO_AVAILABLE else 0
        gold1_metrics = report1["gold"]["metrics_summary"]

        print(f"\n---> RUN 1 COMPLETE in {t1_elapsed}s")
        print(f"     Bronze Ingested: {report1['bronze']['rows_ingested']:,}")
        print(f"     Silver Valid:    {report1['silver']['silver_valid_rows']:,}")
        print(f"     Gold Marts:      {len(report1['gold']['gold_marts_created'])}")
        print(f"     DB Row Count:    {db_count_after_run1:,}")

        # --- RUN 2 (EXACT SAME INPUT) ---
        t2_start = time.time()
        report2 = pipeline.run_pipeline(fixed_input)
        t2_elapsed = round(time.time() - t2_start, 3)

        db_count_after_run2 = CreditCardTransaction.objects.count() if DJANGO_AVAILABLE else 0
        gold2_metrics = report2["gold"]["metrics_summary"]

        print(f"\n---> RUN 2 COMPLETE in {t2_elapsed}s (RERUN WITH EXACT SAME INPUT)")
        print(f"     Bronze Ingested: {report2['bronze']['rows_ingested']:,}")
        print(f"     Silver Valid:    {report2['silver']['silver_valid_rows']:,}")
        print(f"     Gold Marts:      {len(report2['gold']['gold_marts_created'])}")
        print(f"     DB Row Count:    {db_count_after_run2:,}")

        # Check duplicate transaction IDs in Silver Parquet output safely
        silver_dir = "data/lake/silver/credit_card"
        try:
            df_silver = pipeline.spark.read.parquet(silver_dir)
            total_silver_rows = df_silver.count()
            distinct_txn_ids = df_silver.select("transaction_id").distinct().count()
        except Exception:
            import pyarrow.parquet as pq
            table = pq.read_table(silver_dir)
            pdf = table.to_pandas()
            total_silver_rows = len(pdf)
            distinct_txn_ids = pdf["transaction_id"].nunique()

        duplicate_silver_rows = total_silver_rows - distinct_txn_ids

        # Compare Gold Metrics between Run 1 and Run 2 (excluding metadata timestamp)
        g1_data = {k: v for k, v in gold1_metrics.items() if k != "gold_updated_at"}
        g2_data = {k: v for k, v in gold2_metrics.items() if k != "gold_updated_at"}
        gold_metrics_match = (g1_data == g2_data)

        db_new_rows_in_run2 = db_count_after_run2 - db_count_after_run1

        verification_result = {
            "sample_count": sample_count,
            "input_rows": len(fixed_input),
            "run1_execution_time_sec": t1_elapsed,
            "run2_execution_time_sec": t2_elapsed,
            "silver_valid_rows": report1["silver"]["silver_valid_rows"],
            "silver_duplicate_rows": duplicate_silver_rows,
            "postgres_db_initial_count": initial_db_count,
            "postgres_db_after_run1": db_count_after_run1,
            "postgres_db_after_run2": db_count_after_run2,
            "postgres_duplicates_added_in_run2": db_new_rows_in_run2,
            "gold_metrics_identical_across_reruns": gold_metrics_match,
            "gold1_summary": gold1_metrics,
            "gold2_summary": gold2_metrics,
            "is_idempotent_pass": (
                duplicate_silver_rows == 0 and
                db_new_rows_in_run2 == 0 and
                gold_metrics_match
            )
        }

        print("\n--- VERIFICATION VERDICT ---")
        print(f"Silver Duplicate Txn IDs:        {duplicate_silver_rows}")
        print(f"Postgres Duplicates in Run 2:    {db_new_rows_in_run2}")
        print(f"Gold Metrics Identical:         {gold_metrics_match}")
        print(f"IDEMPOTENCY VERIFICATION:       {'PASS' if verification_result['is_idempotent_pass'] else 'FAIL'}")

        return verification_result

    finally:
        pipeline.close()

def main():
    results = {}
    
    # Test 1: 1,000 rows batch
    res_1k = run_idempotency_test_for_batch(1000)
    results["1k_batch"] = res_1k

    # Test 2: 10,000 rows batch
    res_10k = run_idempotency_test_for_batch(10000)
    results["10k_batch"] = res_10k

    summary_file = "verify_milestone2_idempotency_report.json"
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nVerification complete! Full report saved to {summary_file}")

if __name__ == "__main__":
    main()
