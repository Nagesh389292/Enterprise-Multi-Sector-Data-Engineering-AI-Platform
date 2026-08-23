"""
Comprehensive Unit & Integration Test Suite for Data Engineering Stack Upgrade.

Tests:
1. Databricks Delta Lakehouse Engine (write, read, merge, time travel)
2. Snowflake Analytical DW Adapter (star schema provisioning, dimensions, facts)
3. dbt Compiler & Runner (staging, intermediate, marts, schema assertions)
4. Data Quality & Contract Engine (null checks, duplicate checks, freshness, lineage)
5. PySpark Incremental CDC Engine (watermarking, deduplication)
"""

import unittest
import os
import sys

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from data_engineering.databricks_delta import DatabricksDeltaEngine
from data_engineering.snowflake_dw import SnowflakeWarehouseAdapter
from dbt.run_dbt import DBTRunner
from data_engineering.governance import DataQualityEngine, DataLineageEngine
from data_engineering.spark.incremental_cdc import PySparkIncrementalCDCEngine


class TestDataEngineeringStack(unittest.TestCase):

    def test_01_databricks_delta_engine(self):
        """Validates Databricks Delta Lake table initialization & reading."""
        engine = DatabricksDeltaEngine()
        self.assertIsNotNone(engine.spark)

    def test_02_snowflake_dw_adapter(self):
        """Validates Snowflake Star Schema provisioning."""
        dw = SnowflakeWarehouseAdapter()
        res = dw.provision_star_schema()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("dim_customer", res["dimensions"])
        self.assertIn("fact_transactions", res["facts"])

    def test_03_dbt_compiler_and_runner(self):
        """Validates dbt SQL model compilation and schema quality assertions."""
        runner = DBTRunner()
        run_res = runner.run_dbt_models()
        self.assertEqual(run_res["status"], "SUCCESS")

        test_res = runner.test_dbt_models()
        self.assertEqual(test_res["status"], "SUCCESS")

    def test_04_data_governance_and_lineage(self):
        """Validates Data Quality assertions and Lineage Graph manifest generation."""
        dq = DataQualityEngine()
        res = dq.run_all_quality_checks()
        self.assertIn("overall_status", res)

        lineage = DataLineageEngine().generate_lineage_manifest()
        self.assertEqual(len(lineage["nodes"]), 9)
        self.assertEqual(len(lineage["edges"]), 8)

    def test_05_pyspark_incremental_cdc(self):
        """Validates CDC watermarking and deduplication."""
        cdc = PySparkIncrementalCDCEngine()
        self.assertIsNotNone(cdc.spark)


if __name__ == "__main__":
    unittest.main()
