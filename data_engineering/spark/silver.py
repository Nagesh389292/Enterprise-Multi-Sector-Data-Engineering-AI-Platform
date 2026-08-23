"""
PySpark Silver Layer Transformation Module.
Cleans Bronze Parquet data, performs schema validation, and extracts engineered features using PySpark DataFrames & Window Functions.
"""

import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

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


class SparkSilverTransformation:
    """Transforms Bronze Parquet into Silver feature-enriched Parquet dataset using PySpark."""
    def __init__(
        self,
        spark: Optional[SparkSession] = None,
        bronze_dir: str = "data/lake/bronze/credit_card",
        output_dir: str = "data/lake/silver/credit_card"
    ):
        self.spark = spark or get_spark_session("SilverTransformation")
        self.bronze_dir = bronze_dir
        self.output_dir = output_dir

    def process_silver_layer(self) -> Dict[str, Any]:
        """Reads Bronze Parquet data, cleans records, extracts window features, and saves to Silver Parquet."""
        if not os.path.exists(self.bronze_dir):
            raise FileNotFoundError(f"Bronze path does not exist: {self.bronze_dir}")

        try:
            df_bronze = self.spark.read.parquet(self.bronze_dir)
        except Exception:
            import pyarrow.parquet as pq
            table = pq.read_table(self.bronze_dir)
            pdf = table.to_pandas()
            df_bronze = self.spark.createDataFrame(pdf)

        total_bronze_rows = df_bronze.count()

        # Step 1: Validation & Data Cleaning (filter valid amounts & drop duplicates)
        df_valid = (
            df_bronze
            .filter((F.col("amount").isNotNull()) & (F.col("amount") > 0))
            .dropDuplicates(["transaction_id"])
        )
        valid_rows = df_valid.count()
        quarantined_count = total_bronze_rows - valid_rows

        # Step 2: PySpark Window Operations for Streaming & Historical Features
        cust_window = Window.partitionBy("customer_id")
        
        df_silver = (
            df_valid
            # Calculate customer mean and stddev spend
            .withColumn("customer_avg_amount", F.avg("amount").over(cust_window))
            .withColumn("customer_std_amount", F.coalesce(F.stddev("amount").over(cust_window), F.lit(1.0)))
            # Amount Z-score
            .withColumn(
                "amount_zscore",
                F.round((F.col("amount") - F.col("customer_avg_amount")) / (F.col("customer_std_amount") + F.lit(0.001)), 4)
            )
            # Transaction Velocity (Count of txns for same customer)
            .withColumn("velocity_5m", F.count("transaction_id").over(cust_window))
            # Anomaly Risk Flags
            .withColumn(
                "is_unusual_location",
                F.when(F.col("location").isin(["London", "Unknown IP", "New York"]), 1).otherwise(0)
            )
            .withColumn(
                "is_new_device",
                F.when(F.col("device_id").rlike("DEV-9[0-9]{2}"), 1).otherwise(0)
            )
            .withColumn(
                "is_high_velocity",
                F.when(F.col("velocity_5m") > 3, 1).otherwise(0)
            )
            # Silver Operational Metadata
            .withColumn("silver_processed_at", F.lit(datetime.now(timezone.utc).isoformat()))
        )

        save_dataframe_as_parquet(df_silver, self.output_dir, partition_cols=["year", "month"])

        return {
            "layer": "SILVER",
            "status": "SUCCESS",
            "bronze_total_rows": total_bronze_rows,
            "silver_valid_rows": valid_rows,
            "quarantined_rows": quarantined_count,
            "output_path": self.output_dir,
            "features_engineered": [
                "customer_avg_amount", "customer_std_amount", "amount_zscore",
                "velocity_5m", "is_unusual_location", "is_new_device", "is_high_velocity"
            ]
        }

if __name__ == "__main__":
    spark = get_spark_session("SilverTest")
    silver = SparkSilverTransformation(spark)
    res = silver.process_silver_layer()
    print(res)
    spark.stop()
