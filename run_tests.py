"""
Master Test Runner Script for Enterprise Platform Test Suite.
Includes Data Quality Engine, OGD Healthcare Ingestion, Credit Card Fraud Vertical Slice, and PySpark Data Lake Medallion pipeline tests.
"""
import sys
import unittest

sys.path.insert(0, ".")

from tests.test_validation import (
    test_credit_card_validation_pass,
    test_credit_card_validation_quarantine,
    test_banking_validation_range_and_business_rules
)
from tests.test_ogd_ingestion import TestOGDHealthcareIngestion
from tests.test_credit_card_slice import TestCreditCardVerticalSlice
from tests.test_spark_pipeline import TestPySparkMedallionPipeline
from tests.test_ml_engineering import TestMLEngineering
from tests.test_ai_copilot import TestAICopilotRAG
from tests.test_real_world_datasets import TestRealWorldDatasets
from tests.test_bi_superset import TestBISuperset
from tests.test_advanced_analytics import TestAdvancedAnalytics
from tests.test_cloud_cicd import TestCloudCICD
from tests.test_deep_learning_nlp import TestDeepLearningNLP
from tests.test_data_engineering_stack import TestDataEngineeringStack
from tests.test_databricks_integration import TestDatabricksIntegration
from tests.test_live_public_feeds import TestLivePublicFeeds

class DataQualityEngineTestCase(unittest.TestCase):
    def test_pass(self):
        test_credit_card_validation_pass()

    def test_quarantine(self):
        test_credit_card_validation_quarantine()

    def test_banking(self):
        test_banking_validation_range_and_business_rules()

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(DataQualityEngineTestCase))
    suite.addTests(loader.loadTestsFromTestCase(TestOGDHealthcareIngestion))
    suite.addTests(loader.loadTestsFromTestCase(TestCreditCardVerticalSlice))
    suite.addTests(loader.loadTestsFromTestCase(TestPySparkMedallionPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestMLEngineering))
    suite.addTests(loader.loadTestsFromTestCase(TestAICopilotRAG))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldDatasets))
    suite.addTests(loader.loadTestsFromTestCase(TestBISuperset))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedAnalytics))
    suite.addTests(loader.loadTestsFromTestCase(TestCloudCICD))
    suite.addTests(loader.loadTestsFromTestCase(TestDeepLearningNLP))
    suite.addTests(loader.loadTestsFromTestCase(TestDataEngineeringStack))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabricksIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestLivePublicFeeds))
    return suite


if __name__ == "__main__":
    unittest.main()
