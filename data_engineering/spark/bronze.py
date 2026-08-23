"""
PySpark Bronze Layer Module.
Ingests raw Credit Card transactions, enforces schema, appends metadata, and writes partitioned Parquet datasets.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType
)

from data_engineering.spark.spark_session import get_spark_session

# Explicit PySpark Schema Enforcement
CREDIT_CARD_BRONZE_SCHEMA = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("event_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("card_type", StringType(), True),
    StructField("merchant", StringType(), True),
    StructField("location", StringType(), True),
    StructField("device_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("is_fraud_ground_truth", IntegerType(), True),
])

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


class SparkBronzeIngestion:
    """Ingests raw JSON transactions into Bronze Parquet Data Lake layer using PySpark."""
    def __init__(self, spark: Optional[SparkSession] = None, output_base_dir: str = "data/lake/bronze/credit_card"):
        self.spark = spark or get_spark_session("BronzeIngestion")
        self.output_base_dir = output_base_dir

    def process_raw_data(self, input_path_or_records: Any, source_name: str = "credit_card_stream") -> Dict[str, Any]:
        """Ingests raw records or JSON file into Bronze Parquet lake."""
        if isinstance(input_path_or_records, str) and os.path.exists(input_path_or_records):
            df_raw = self.spark.read.schema(CREDIT_CARD_BRONZE_SCHEMA).json(input_path_or_records)
        elif isinstance(input_path_or_records, list):
            df_raw = self.spark.createDataFrame(input_path_or_records, schema=CREDIT_CARD_BRONZE_SCHEMA)
        else:
            raise ValueError("Input must be a valid JSON filepath or list of dict records.")

        now_iso = datetime.now(timezone.utc).isoformat()
        
        # Add metadata & partition columns (year/month)
        df_bronze = (
            df_raw
            .withColumn("source", F.lit(source_name))
            .withColumn("ingestion_timestamp", F.coalesce(F.col("timestamp"), F.lit(now_iso)))
            .withColumn("processing_timestamp", F.lit(now_iso))
            .withColumn("pipeline_version", F.lit("v2.0-pyspark"))
            .withColumn("ts_parsed", F.to_timestamp(F.col("timestamp")))
            .withColumn("year", F.coalesce(F.year(F.col("ts_parsed")), F.lit(2026)))
            .withColumn("month", F.coalesce(F.month(F.col("ts_parsed")), F.lit(8)))
            .drop("ts_parsed")
        )

        row_count = df_bronze.count()
        save_dataframe_as_parquet(df_bronze, self.output_base_dir, partition_cols=["year", "month"])

        return {
            "layer": "BRONZE",
            "status": "SUCCESS",
            "rows_ingested": row_count,
            "output_path": self.output_base_dir,
            "partition_cols": ["year", "month"]
        }

if __name__ == "__main__":
    spark = get_spark_session("BronzeTest")
    sample_records = [
        {
            "transaction_id": "TXN-1001",
            "event_id": "TXN-1001",
            "customer_id": "CUST-501",
            "amount": 250.50,
            "card_type": "VISA",
            "merchant": "Electronics",
            "location": "Mumbai",
            "device_id": "DEV-101",
            "timestamp": "2026-08-23T00:00:00Z",
            "is_fraud_ground_truth": 0
        }
    ]
    bronze = SparkBronzeIngestion(spark)
    res = bronze.process_raw_data(sample_records)
    print(res)
    spark.stop()
