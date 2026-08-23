"""
Unit tests for Live External Public Feeds Ingestion Module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from data_engineering.ingestion.live_public_feeds import LivePublicDataIngestor


class TestLivePublicFeeds(unittest.TestCase):
    """Test suite for GDELT, OpenAQ, RBI Macro, and Alpha Vantage live public feeds."""

    def setUp(self):
        self.ingestor = LivePublicDataIngestor()

    def test_rbi_macro_indicators(self):
        """Validates RBI / Macro Economic indicators data structure."""
        res = self.ingestor.fetch_rbi_macro_indicators()
        self.assertIn("repo_rate_pct", res)
        self.assertEqual(res["repo_rate_pct"], 6.50)
        self.assertIn("banking_default_stress_index", res)

    def test_gdelt_fallback(self):
        """Validates GDELT fallback mechanism when network is mock-disabled."""
        with patch.object(self.ingestor, "_http_get_json", return_value=None):
            res = self.ingestor.fetch_gdelt_news_sentiment()
            self.assertEqual(res["status"], "FALLBACK_BASELINE")
            self.assertGreaterEqual(len(res["articles"]), 1)

    def test_openaq_fallback(self):
        """Validates OpenAQ fallback mechanism when network is mock-disabled."""
        with patch.object(self.ingestor, "_http_get_json", return_value=None):
            res = self.ingestor.fetch_openaq_air_quality("Delhi")
            self.assertEqual(res["status"], "FALLBACK_BASELINE")
            self.assertIn("respiratory_admission_risk_multiplier", res)

    def test_alpha_vantage_fallback(self):
        """Validates Alpha Vantage fallback mechanism."""
        res = self.ingestor._alpha_vantage_fallback("IBM")
        self.assertEqual(res["symbol"], "IBM")
        self.assertEqual(res["status"], "FALLBACK_BASELINE")

    def test_ingest_all_live_feeds(self):
        """Validates master ingest_all_live_feeds returns all 4 feeds."""
        res = self.ingestor.ingest_all_live_feeds()
        self.assertIn("gdelt", res)
        self.assertIn("openaq", res)
        self.assertIn("rbi_macro", res)
        self.assertIn("alpha_vantage", res)


if __name__ == "__main__":
    unittest.main()
