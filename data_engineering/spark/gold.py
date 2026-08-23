"""
PySpark Gold Data Mart Aggregation Module.
Creates Gold analytical data marts (gold_fraud_metrics, gold_customer_risk, gold_merchant_risk, gold_daily_transactions)
from Silver Parquet datasets and syncs with PostgreSQL / Django database.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F

from data_engineering.spark.spark_session import get_spark_session

def save_dataframe_as_parquet(df: DataFrame, output_dir: str, partition_cols: Optional[List[str]] = None):
    """Saves PySpark DataFrame to Parquet dataset with PyArrow fallback."""
    os.makedirs(output_dir, exist_ok=True)
    try:
        writer = df.write.mode("overwrite")
        if partition_cols:
            writer = writer.partitionBy(*partition_cols)
        writer.parquet(output_dir)
    except Exception:
        pdf = df.toPandas()
        import pyarrow as pa
        import pyarrow.parquet as pq
        table = pa.Table.from_pandas(pdf)
        if partition_cols and len(pdf) > 0:
            pq.write_to_dataset(table, root_path=output_dir, partition_cols=partition_cols)
        else:
            pq.write_table(table, os.path.join(output_dir, "data.parquet"))


class SparkGoldAggregation:
    """Aggregates Silver feature tables into Gold Data Marts using PySpark."""
    def __init__(
        self,
        spark: Optional[SparkSession] = None,
        silver_dir: str = "data/lake/silver/credit_card",
        gold_base_dir: str = "data/lake/gold"
    ):
        self.spark = spark or get_spark_session("GoldAggregation")
        self.silver_dir = silver_dir
        self.gold_base_dir = gold_base_dir

    def process_gold_layer(self) -> Dict[str, Any]:
        """Reads Silver Parquet data and produces 4 Gold analytical data marts."""
        if not os.path.exists(self.silver_dir):
            raise FileNotFoundError(f"Silver path does not exist: {self.silver_dir}")

        try:
            df_silver = self.spark.read.parquet(self.silver_dir)
        except Exception:
            import pyarrow.parquet as pq
            table = pq.read_table(self.silver_dir)
            pdf = table.to_pandas()
            df_silver = self.spark.createDataFrame(pdf)

        total_silver_rows = df_silver.count()

        os.makedirs(self.gold_base_dir, exist_ok=True)

        # 1. Gold Fraud Metrics Mart
        df_fraud_metrics = (
            df_silver
            .agg(
                F.count("transaction_id").alias("total_transactions"),
                F.round(F.sum("amount"), 2).alias("total_volume_usd"),
                F.sum("is_fraud_ground_truth").alias("total_fraud_transactions"),
                F.round(F.sum(F.when(F.col("is_fraud_ground_truth") == 1, F.col("amount")).otherwise(0.0)), 2).alias("total_fraud_volume_usd"),
                F.round(F.avg("amount"), 2).alias("avg_transaction_amount"),
                F.round((F.sum("is_fraud_ground_truth") / F.count("transaction_id")) * 100.0, 2).alias("fraud_rate_pct")
            )
            .withColumn("gold_updated_at", F.lit(datetime.now(timezone.utc).isoformat()))
        )
        gold_metrics_path = os.path.join(self.gold_base_dir, "gold_fraud_metrics")
        save_dataframe_as_parquet(df_fraud_metrics, gold_metrics_path)

        # 2. Gold Customer Risk Mart
        df_customer_risk = (
            df_silver
            .groupBy("customer_id")
            .agg(
                F.count("transaction_id").alias("txn_count"),
                F.round(F.sum("amount"), 2).alias("total_spent"),
                F.round(F.max("amount"), 2).alias("max_single_txn"),
                F.sum("is_fraud_ground_truth").alias("fraud_count"),
                F.round(F.avg("amount_zscore"), 2).alias("avg_zscore"),
                F.max("is_unusual_location").alias("has_unusual_location"),
                F.max("is_new_device").alias("has_new_device")
            )
            .withColumn(
                "risk_score",
                F.round(
                    F.least(
                        F.lit(100.0),
                        (F.col("fraud_count") * 40.0) +
                        (F.col("has_unusual_location") * 25.0) +
                        (F.col("has_new_device") * 20.0) +
                        (F.when(F.col("avg_zscore") > 2.0, 15.0).otherwise(0.0))
                    ), 2
                )
            )
            .withColumn(
                "risk_category",
                F.when(F.col("risk_score") >= 75.0, "CRITICAL")
                .when(F.col("risk_score") >= 45.0, "HIGH")
                .when(F.col("risk_score") >= 20.0, "MEDIUM")
                .otherwise("LOW")
            )
            .withColumn("gold_updated_at", F.lit(datetime.now(timezone.utc).isoformat()))
        )
        gold_cust_path = os.path.join(self.gold_base_dir, "gold_customer_risk")
        save_dataframe_as_parquet(df_customer_risk, gold_cust_path)

        # 3. Gold Merchant Risk Mart
        df_merchant_risk = (
            df_silver
            .groupBy("merchant")
            .agg(
                F.count("transaction_id").alias("total_transactions"),
                F.round(F.sum("amount"), 2).alias("total_volume"),
                F.sum("is_fraud_ground_truth").alias("fraud_count"),
                F.round((F.sum("is_fraud_ground_truth") / F.count("transaction_id")) * 100.0, 2).alias("merchant_fraud_rate_pct")
            )
            .withColumn("gold_updated_at", F.lit(datetime.now(timezone.utc).isoformat()))
        )
        gold_merch_path = os.path.join(self.gold_base_dir, "gold_merchant_risk")
        save_dataframe_as_parquet(df_merchant_risk, gold_merch_path)

        # 4. Gold Daily Transactions Mart
        df_daily_txns = (
            df_silver
            .select(
                "transaction_id", "customer_id", "amount", "card_type",
                "merchant", "location", "device_id", "timestamp",
                "is_fraud_ground_truth", "customer_avg_amount", "amount_zscore",
                "velocity_5m", "is_unusual_location", "is_new_device", "is_high_velocity",
                "year", "month"
            )
            .withColumn("gold_updated_at", F.lit(datetime.now(timezone.utc).isoformat()))
        )
        gold_daily_path = os.path.join(self.gold_base_dir, "gold_daily_transactions")
        save_dataframe_as_parquet(df_daily_txns, gold_daily_path, partition_cols=["year", "month"])

        # Generate Gold JSON Summary for REST API & BI Layer
        metrics_dict = df_fraud_metrics.first().asDict() if df_fraud_metrics.count() > 0 else {}
        gold_json_path = os.path.join(self.gold_base_dir, "gold_fraud_summary.json")
        with open(gold_json_path, "w") as f:
            json.dump(metrics_dict, f, indent=2)

        return {
            "layer": "GOLD",
            "status": "SUCCESS",
            "silver_input_rows": total_silver_rows,
            "gold_marts_created": [
                "gold_fraud_metrics",
                "gold_customer_risk",
                "gold_merchant_risk",
                "gold_daily_transactions"
            ],
            "metrics_summary": metrics_dict,
            "output_dir": self.gold_base_dir
        }

if __name__ == "__main__":
    spark = get_spark_session("GoldTest")
    gold = SparkGoldAggregation(spark)
    res = gold.process_gold_layer()
    print(res)
    spark.stop()
