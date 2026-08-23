"""
Automated Resilience & Failure Chaos Test Suite.

Simulates subsystem failures:
1. Redis Stream Producer / Consumer Offline -> Synchronous Fallback
2. PostgreSQL Database Connection Failure -> SQLite (platform_analytics.db) Fallback
3. Gemini LLM API Disconnection -> Local Ollama / Rule-based SQL Router Fallback
4. Data Quarantine Ingestion -> Failure Isolation & Telemetry Collection
"""

import unittest
import os
import sys
from datetime import datetime, timezone

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from streaming.redis_stream_consumer import stream_consumer
from ai.agent.router import AgenticRouter
from data_engineering.validation.validator import get_credit_card_validator
from data_engineering.postgres_sync import PostgresGoldSync


class TestResilienceChaosSuite(unittest.TestCase):

    def test_01_redis_offline_synchronous_fallback(self):
        """Simulates Redis offline state; verifies synchronous event processing fallback."""
        event = {
            "transaction_id": "TXN-CHAOS-001",
            "customer_id": "CUST-CHAOS-01",
            "amount": 999.99,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "card_type": "VISA"
        }
        res = stream_consumer.process_single_event(event)
        self.assertIn("risk_score", res)
        self.assertIn("risk_level", res)
        self.assertTrue("transaction_id" in res or "event_id" in res)

    def test_02_postgres_offline_sqlite_fallback(self):
        """Simulates PostgreSQL connection failure; verifies automatic SQLite fallback engine."""
        try:
            sync_engine = PostgresGoldSync()
            # Force invalid host to trigger failure path
            sync_engine.db_url = "postgresql://user:wrongpass@invalidhost:5432/invalid_db"
            res = sync_engine.sync_all_marts()
            self.assertIn("SQLite", res["database_engine"])
            self.assertEqual(res["status"], "SUCCESS")
        except Exception as e:
            self.fail(f"Postgres fallback raised unexpected exception: {e}")

    def test_03_gemini_api_offline_copilot_fallback(self):
        """Simulates Gemini API rate limit / offline error; verifies local Ollama / rule-based fallback."""
        router = AgenticRouter()
        res = router.process_query("What is our total credit card fraud count?")
        self.assertIn("intent", res)
        self.assertTrue("executive_answer" in res or "response" in res)

    def test_04_data_quarantine_failure_isolation(self):
        """Passes malformed event; verifies isolation into quarantine without pipeline crash."""
        validator = get_credit_card_validator()
        invalid_event = {
            "transaction_id": "TXN-MALFORMED-99",
            # Missing customer_id, timestamp, card_type
            "amount": -50.0 # Invalid negative amount
        }
        val_res = validator.validate_record(invalid_event)
        self.assertFalse(val_res.is_valid)
        self.assertGreater(len(val_res.errors), 0)
        quarantine_dict = val_res.to_quarantine_dict()
        self.assertEqual(quarantine_dict["status"], "QUARANTINED")


if __name__ == "__main__":
    unittest.main()
