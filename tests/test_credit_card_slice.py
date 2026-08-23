"""
Automated Integration & Unit Test Suite for Credit Card Fraud Real-Time Vertical Slice.
Verifies event stream generation -> validation -> feature extraction -> ML inference -> telemetry.
"""

import unittest
from streaming.redis_stream_producer import RedisStreamProducer
from streaming.redis_stream_consumer import stream_consumer
from ml.feature_engineering import feature_store
from ml.fraud_detection import FraudDetectionEngine

class TestCreditCardVerticalSlice(unittest.TestCase):
    def setUp(self):
        self.producer = RedisStreamProducer()
        self.consumer = stream_consumer
        self.ml_engine = FraudDetectionEngine()

    def test_producer_event_generation(self):
        """Tests that event producer generates expected schema events."""
        events = self.producer.generate_live_burst(count=3, fraud_spike=False)
        self.assertEqual(len(events), 3)
        self.assertIn("event_id", events[0])
        self.assertIn("amount", events[0])
        self.assertIn("location", events[0])

    def test_realtime_feature_engineering(self):
        """Tests calculation of velocity_5m, amount_zscore, and risk flags."""
        evt1 = {"event_id": "TXN_T1", "customer_id": "CUST_TEST_1", "amount": 100.0, "location": "Mumbai", "device_id": "DEV_1", "card_type": "VISA"}
        evt2 = {"event_id": "TXN_T2", "customer_id": "CUST_TEST_1", "amount": 95000.0, "location": "London", "device_id": "DEV_99", "card_type": "VISA"}

        f1 = feature_store.extract_features(evt1)
        f2 = feature_store.extract_features(evt2)

        self.assertEqual(f1["velocity_5m"], 1)
        self.assertEqual(f2["velocity_5m"], 2)
        self.assertEqual(f2["is_unusual_location"], 1)
        self.assertEqual(f2["is_new_device"], 1)

    def test_fraud_detection_ml_inference(self):
        """Tests XGBoost & PyTorch Autoencoder risk prediction and explanation generation."""
        high_risk_evt = {
            "event_id": "TXN_HIGH",
            "customer_id": "C1029",
            "amount": 84500.0,
            "merchant": "Electronics",
            "location": "London",
            "device_id": "DEV-999",
            "card_type": "VISA"
        }
        res = self.ml_engine.predict(high_risk_evt)

        self.assertIn("risk_score", res)
        self.assertIn("risk_level", res)
        self.assertEqual(res["risk_level"], "HIGH")
        self.assertGreater(len(res["explanation_reasons"]), 0)

    def test_end_to_end_stream_consumer_telemetry(self):
        """Tests end-to-end stream consumer processing and operational telemetry updating."""
        evt = {
            "event_id": "TXN_CONSUMER_TEST",
            "transaction_id": "TXN_CONSUMER_TEST",
            "customer_id": "CUST_999",
            "amount": 250.0,
            "merchant": "Dining",
            "location": "Bengaluru",
            "device_id": "DEV-101",
            "card_type": "VISA",
            "timestamp": "2026-08-23T00:00:00Z"
        }
        processed = self.consumer.process_single_event(evt)
        telemetry = self.consumer.get_live_telemetry()

        self.assertEqual(processed["status"], "PROCESSED")
        self.assertGreater(telemetry["total_processed_events"], 0)
        self.assertGreaterEqual(telemetry["data_quality_compliance_pct"], 0.0)

if __name__ == "__main__":
    unittest.main()
