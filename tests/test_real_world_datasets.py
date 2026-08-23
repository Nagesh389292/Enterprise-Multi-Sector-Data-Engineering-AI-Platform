"""
Unit Test Suite for Milestone 5: Real-World Multi-Sector Data Integration.
"""

import os
import json
import unittest
from data_engineering.ingestion.ingest_real_world_datasets import ingest_all_real_world_datasets
from data_engineering.spark.multi_sector_pipeline import MultiSectorSparkPipeline
from data_engineering.postgres_sync import PostgresGoldSync
from ml.multi_sector_ml import MultiSectorMLEngine
from ai.agent.metrics_tool import MetricsTool


class TestRealWorldDatasets(unittest.TestCase):
    """Test suite for Real-World Multi-Sector datasets, Medallion pipeline, and ML models."""

    def test_01_real_world_ingestion(self):
        """Verifies raw CSV and JSON dataset creation for all 6 sectors."""
        ingest_all_real_world_datasets()
        
        sectors = ["credit_card", "banking", "healthcare", "clinical", "insurance", "retail"]
        for sector in sectors:
            sector_dir = os.path.join(os.getcwd(), "data", "raw", "real_world", sector)
            self.assertTrue(os.path.exists(sector_dir), f"Missing raw directory for sector {sector}")
            files = os.listdir(sector_dir)
            self.assertGreater(len(files), 0, f"No raw data files generated for sector {sector}")

    def test_02_pyspark_medallion_pipeline(self):
        """Verifies PySpark Medallion pipeline transforms real data into Bronze, Silver, and Gold Parquet."""
        pipeline = MultiSectorSparkPipeline()
        res = pipeline.run_all_pipelines()
        
        self.assertIn("credit_card", res)
        self.assertIn("banking", res)
        self.assertIn("healthcare", res)
        self.assertIn("clinical", res)
        self.assertIn("insurance", res)
        self.assertIn("retail", res)
        self.assertGreater(res["credit_card"]["total_transactions"], 0)

    def test_03_postgres_db_sync(self):
        """Verifies sync of Gold Data Marts into platform analytics database."""
        sync = PostgresGoldSync()
        res = sync.sync_all_marts()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["synced_sectors_count"], 6)

    def test_04_multi_sector_ml_training(self):
        """Verifies model training and benchmark evaluations on real datasets."""
        ml_engine = MultiSectorMLEngine()
        report = ml_engine.train_all_models()
        
        self.assertIn("credit_card", report)
        self.assertIn("banking", report)
        self.assertIn("clinical", report)
        self.assertGreater(report["credit_card"]["rf_metrics"]["f1_score"], 0.5)

    def test_05_copilot_real_data_grounding(self):
        """Verifies MetricsTool returns ground-truth multi-sector metrics from Lakehouse Gold."""
        metrics_tool = MetricsTool()
        res = metrics_tool.get_fraud_summary_metrics()
        self.assertIn("total_transactions", res)
        self.assertGreater(res["total_transactions"], 0)


if __name__ == "__main__":
    unittest.main()
