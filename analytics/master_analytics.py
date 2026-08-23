"""
Master Enterprise Analytics Platform Orchestrator (`analytics/master_analytics.py`).

Consolidates all 6 sector analytics engines:
1. Credit Card Fraud Anomaly Detection
2. Banking Customer Credit Risk Segmentation
3. Healthcare Bed Capacity Forecasting
4. Clinical EHR Readmission Risk Calibration
5. Insurance Claims Fraud Investigation Queue
6. Retail Sales & Demand Forecasting
"""

import os
import sys
import json
import pandas as pd
from typing import Dict, Any

sys.path.insert(0, os.getcwd())

from analytics.anomaly.fraud_anomaly_detector import FraudAnomalyDetector
from analytics.segmentation.customer_segmentation import CustomerSegmentationEngine
from analytics.forecasting.capacity_forecaster import CapacityForecaster
from analytics.calibration.readmission_calibrator import ReadmissionCalibrator
from analytics.anomaly.insurance_claims_queue import InsuranceClaimsQueueEngine
from analytics.forecasting.demand_forecaster import RetailDemandForecaster

RAW_DIR = os.path.join(os.getcwd(), "data", "raw", "real_world")
OUTPUT_PATH = os.path.join(os.getcwd(), "data", "lake", "gold", "master_analytics_results.json")


class MasterAnalyticsPlatform:
    """Orchestrates analytics runs across all 6 enterprise sectors."""

    def run_all_analytics(self) -> Dict[str, Any]:
        """Runs complete multi-sector predictive & prescriptive analytics pipeline."""
        results = {}

        # 1. Credit Card Fraud Anomaly Detection
        cc_csv = os.path.join(RAW_DIR, "credit_card", "credit_card_real.csv")
        if os.path.exists(cc_csv):
            df_cc = pd.read_csv(cc_csv)
            detector = FraudAnomalyDetector()
            results["credit_card_fraud_anomaly"] = detector.analyze_fraud_trend(df_cc)

        # 2. Banking Customer Risk Segmentation
        bank_csv = os.path.join(RAW_DIR, "banking", "banking_loan_risk_real.csv")
        if os.path.exists(bank_csv):
            df_bank = pd.read_csv(bank_csv)
            segmenter = CustomerSegmentationEngine()
            results["banking_customer_segmentation"] = segmenter.segment_customers(df_bank)

        # 3. Healthcare Capacity Forecasting
        health_json = os.path.join(RAW_DIR, "healthcare", "healthcare_ogd_real.json")
        if os.path.exists(health_json):
            with open(health_json, "r") as f:
                h_data = json.load(f)
            df_health = pd.DataFrame(h_data.get("records", h_data))
            forecaster = CapacityForecaster()
            results["healthcare_capacity_forecasting"] = forecaster.forecast_occupancy(df_health)

        # 4. Clinical Readmission Calibration
        clin_csv = os.path.join(RAW_DIR, "clinical", "clinical_readmission_real.csv")
        if os.path.exists(clin_csv):
            df_clin = pd.read_csv(clin_csv)
            calibrator = ReadmissionCalibrator()
            results["clinical_readmission_calibration"] = calibrator.calibrate_readmission_risk(df_clin)

        # 5. Insurance Claims Fraud Investigation Queue
        ins_csv = os.path.join(RAW_DIR, "insurance", "insurance_claims_real.csv")
        if os.path.exists(ins_csv):
            df_ins = pd.read_csv(ins_csv)
            queue_engine = InsuranceClaimsQueueEngine()
            results["insurance_claims_queue"] = queue_engine.generate_investigation_queue(df_ins)

        # 6. Retail Demand Forecasting
        retail_csv = os.path.join(RAW_DIR, "retail", "retail_sales_real.csv")
        if os.path.exists(retail_csv):
            df_retail = pd.read_csv(retail_csv)
            demand_engine = RetailDemandForecaster()
            results["retail_demand_forecasting"] = demand_engine.forecast_demand(df_retail)

        summary = {
            "status": "SUCCESS",
            "sectors_analyzed_count": len(results),
            "sectors": results
        }

        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print(f"[MasterAnalytics] Successfully executed 6-sector analytics pipeline -> {OUTPUT_PATH}")
        return summary


if __name__ == "__main__":
    platform = MasterAnalyticsPlatform()
    res = platform.run_all_analytics()
    print(res)
