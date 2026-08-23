"""
Unit Test Suite for Milestone 7: Advanced Business Analytics & Time-Series Forecasting.
"""

import os
import unittest
import pandas as pd
from analytics.anomaly.fraud_anomaly_detector import FraudAnomalyDetector
from analytics.segmentation.customer_segmentation import CustomerSegmentationEngine
from analytics.forecasting.capacity_forecaster import CapacityForecaster
from analytics.calibration.readmission_calibrator import ReadmissionCalibrator
from analytics.anomaly.insurance_claims_queue import InsuranceClaimsQueueEngine
from analytics.forecasting.demand_forecaster import RetailDemandForecaster
from analytics.master_analytics import MasterAnalyticsPlatform


class TestAdvancedAnalytics(unittest.TestCase):
    """Unit tests for multi-sector predictive & prescriptive analytics engines."""

    def test_fraud_anomaly_detector(self):
        detector = FraudAnomalyDetector()
        df = pd.DataFrame({
            "Time": list(range(0, 48 * 3600, 3600)),
            "Class": [0, 1] * 24,
            "Amount": [100.0] * 48
        })
        res = detector.analyze_fraud_trend(df)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("latest_baseline_rate_pct", res)

    def test_customer_segmentation(self):
        engine = CustomerSegmentationEngine(n_clusters=3)
        df = pd.DataFrame({
            "Age": [25, 45, 60, 30, 50, 65] * 20,
            "AnnualIncome": [40000, 80000, 120000, 50000, 90000, 130000] * 20,
            "CreditAmount": [5000, 15000, 30000, 6000, 18000, 35000] * 20,
            "DurationMonths": [12, 24, 36, 12, 24, 36] * 20,
            "DefaultRisk": [0, 1, 0, 1, 0, 1] * 20
        })
        res = engine.segment_customers(df)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(len(res["cluster_profiles"]), 3)

    def test_capacity_forecaster(self):
        forecaster = CapacityForecaster(forecast_horizon_days=7)
        df = pd.DataFrame({
            "bed_occupancy_rate_pct": [70.0 + (i % 10) for i in range(30)]
        })
        res = forecaster.forecast_occupancy(df)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(len(res["forecasted_series"]), 7)

    def test_readmission_calibrator(self):
        calibrator = ReadmissionCalibrator()
        df = pd.DataFrame({
            "TimeInHospitalDays": [3, 5, 8, 2, 6] * 10,
            "NumLabProcedures": [30, 45, 60, 20, 50] * 10,
            "NumMedications": [10, 15, 25, 8, 18] * 10,
            "NumDiagnoses": [4, 6, 9, 3, 7] * 10,
            "Readmitted30Days": [0, 1, 1, 0, 1] * 10
        })
        res = calibrator.calibrate_readmission_risk(df)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("optimal_decision_threshold", res)

    def test_insurance_claims_queue(self):
        engine = InsuranceClaimsQueueEngine()
        df = pd.DataFrame({
            "PolicyID": [f"POL-{i}" for i in range(20)],
            "TotalClaimAmount": [5000.0] * 19 + [95000.0],
            "InjuryClaim": [1000.0] * 19 + [40000.0],
            "PropertyClaim": [4000.0] * 19 + [55000.0],
            "CustomerAge": [35] * 20,
            "VehicleAgeYears": [5] * 20,
            "IncidentType": ["Parked Car"] * 20
        })
        res = engine.generate_investigation_queue(df, top_n=5)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(len(res["top_investigation_queue"]), 5)

    def test_retail_demand_forecaster(self):
        forecaster = RetailDemandForecaster(forecast_horizon_invoices=14)
        df = pd.DataFrame({
            "Quantity": [20 + (i % 5) for i in range(40)],
            "TotalSales": [200.0] * 40
        })
        res = forecaster.forecast_demand(df)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(len(res["forecasted_demand_series"]), 14)

    def test_master_analytics(self):
        platform = MasterAnalyticsPlatform()
        res = platform.run_all_analytics()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["sectors_analyzed_count"], 6)


if __name__ == "__main__":
    unittest.main()
