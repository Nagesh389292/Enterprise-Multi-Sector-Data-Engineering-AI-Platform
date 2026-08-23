"""
Unit Test Suite for Milestone 6: Apache Superset BI & Dashboard Layer.
"""

import os
import unittest
from bi.dashboard_configs import get_all_dashboard_configs
from bi.superset_init import SupersetInitializer


class TestBISuperset(unittest.TestCase):
    """Unit tests for Superset BI configurations and provisioning."""

    def test_dashboard_configs_count(self):
        configs = get_all_dashboard_configs()
        self.assertEqual(len(configs), 7)
        self.assertIn("executive_command_center", configs)
        self.assertIn("fraud_intelligence", configs)
        self.assertIn("banking_credit_risk", configs)
        self.assertIn("healthcare_utilization", configs)
        self.assertIn("clinical_readmission", configs)
        self.assertIn("insurance_claims_fraud", configs)
        self.assertIn("retail_demand_revenue", configs)

    def test_superset_provisioning_export(self):
        init = SupersetInitializer()
        res = init.run_provisioning()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(res["dashboards_provisioned_count"] >= 7)
        self.assertTrue(os.path.exists(res["manifest_file"]))
        if res.get("authenticated"):
            self.assertEqual(res["charts_count"], 9)
            self.assertEqual(res["datasets_count"], 7)
            self.assertEqual(res["databases_count"], 1)


if __name__ == "__main__":
    unittest.main()
