"""
Automated Unit Test Suite for PySpark Data Lake Medallion Pipeline.
Tests SparkSession creation, Bronze Ingestion, Silver Feature Transformations, and Gold Data Mart Aggregations.
"""

import os
import sys
import unittest

sys.path.insert(0, os.getcwd())

from data_engineering.spark.spark_session import get_spark_session
from data_engineering.spark.bronze import SparkBronzeIngestion
from data_engineering.spark.silver import SparkSilverTransformation
from data_engineering.spark.gold import SparkGoldAggregation
from data_engineering.spark.credit_card_pipeline import generate_synthetic_transactions

class TestPySparkMedallionPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = get_spark_session("SparkUnitTestSuite")

    @classmethod
    def tearDownClass(cls):
        if cls.spark:
            cls.spark.stop()

    def test_1_sparksession_creation(self):
        """Tests that PySpark SparkSession initializes properly."""
        self.assertIsNotNone(self.spark)
        self.assertTrue(self.spark.version.startswith("4.") or self.spark.version.startswith("3."))

    def test_2_bronze_ingestion(self):
        """Tests Bronze ingestion schema enforcement and metadata column addition."""
        records = generate_synthetic_transactions(count=20)
        bronze_engine = SparkBronzeIngestion(self.spark, output_base_dir="data/test_lake/bronze")
        res = bronze_engine.process_raw_data(records)

        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["rows_ingested"], 20)
        self.assertTrue(os.path.exists("data/test_lake/bronze"))

    def test_3_silver_transformations(self):
        """Tests Silver data cleaning, validation, and PySpark window feature engineering."""
        silver_engine = SparkSilverTransformation(
            self.spark,
            bronze_dir="data/test_lake/bronze",
            output_dir="data/test_lake/silver"
        )
        res = silver_engine.process_silver_layer()

        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreater(res["silver_valid_rows"], 0)
        self.assertIn("amount_zscore", res["features_engineered"])

    def test_4_gold_data_marts(self):
        """Tests Gold analytical data mart aggregations."""
        gold_engine = SparkGoldAggregation(
            self.spark,
            silver_dir="data/test_lake/silver",
            gold_base_dir="data/test_lake/gold"
        )
        res = gold_engine.process_gold_layer()

        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(len(res["gold_marts_created"]), 4)
        self.assertIn("total_transactions", res["metrics_summary"])

if __name__ == "__main__":
    unittest.main()
