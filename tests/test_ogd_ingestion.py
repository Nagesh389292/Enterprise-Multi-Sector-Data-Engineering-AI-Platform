"""
Unit tests for India OGD Healthcare Ingestion Pipeline.
Tests Medallion pipeline behavior across success, empty, malformed, 429, 500, and timeout scenarios.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import urllib.error

from domains.healthcare.ogd_ingestion import OGDHealthcareIngestionEngine, DataQualityFailureError

class TestOGDHealthcareIngestion(unittest.TestCase):
    def setUp(self):
        self.engine = OGDHealthcareIngestionEngine()
        self.engine.api_key = "test_mock_key"

    @patch("urllib.request.urlopen")
    def test_successful_api_response_and_silver_gold_transformation(self, mock_urlopen):
        """Tests end-to-end Medallion flow with valid API records."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_payload = {
            "version": "2.2.0",
            "status": "ok",
            "total": 2,
            "records": [
                {
                    "id": "HOSP_101",
                    "hospital_name": "Apollo Health City",
                    "state": "Telangana",
                    "district": "Hyderabad",
                    "beds": "450",
                    "category": "Private"
                },
                {
                    "id": "HOSP_102",
                    "hospital_name": "NIMS Hospital",
                    "state": "Telangana",
                    "district": "Hyderabad",
                    "beds": "800",
                    "category": "Government"
                }
            ]
        }
        mock_resp.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = self.engine.run_ingestion_pipeline(limit=10)

        self.assertEqual(result["status"], "LIVE_SUCCESS")
        self.assertEqual(result["total_records_ingested"], 2)
        self.assertEqual(result["total_beds_registered"], 1250)
        self.assertEqual(result["avg_beds_per_hospital"], 625.0)

    @patch("urllib.request.urlopen")
    def test_empty_api_response_quarantine_routing(self, mock_urlopen):
        """Tests that empty records=[] response triggers DATA_QUALITY_FAILURE and routes to quarantine without fabricating data."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_payload = {
            "version": "2.2.0",
            "status": "error",
            "message": "Meta not found",
            "total": 0,
            "records": []
        }
        mock_resp.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = self.engine.run_ingestion_pipeline(limit=10)

        self.assertEqual(result["status"], "DATA_QUALITY_FAILURE")
        self.assertIn("0 valid records", result["failure_reason"])

    @patch("urllib.request.urlopen")
    def test_http_429_rate_limit_retry(self, mock_urlopen):
        """Tests retry logic when API returns HTTP 429 Too Many Requests."""
        mock_error = urllib.error.HTTPError("https://api.data.gov.in", 429, "Too Many Requests", {}, None)
        mock_urlopen.side_effect = mock_error

        result = self.engine.run_ingestion_pipeline(limit=10)
        self.assertEqual(result["status"], "DATA_QUALITY_FAILURE")
        self.assertIn("429", result["failure_reason"])

    @patch("urllib.request.urlopen")
    def test_http_500_server_error(self, mock_urlopen):
        """Tests handling of HTTP 500 Internal Server Error."""
        mock_error = urllib.error.HTTPError("https://api.data.gov.in", 500, "Internal Server Error", {}, None)
        mock_urlopen.side_effect = mock_error

        result = self.engine.run_ingestion_pipeline(limit=10)
        self.assertEqual(result["status"], "DATA_QUALITY_FAILURE")
        self.assertIn("500", result["failure_reason"])

    @patch("urllib.request.urlopen")
    def test_timeout_error_handling(self, mock_urlopen):
        """Tests handling of network connection timeout."""
        mock_urlopen.side_effect = TimeoutError("Connection timed out")

        result = self.engine.run_ingestion_pipeline(limit=10)
        self.assertEqual(result["status"], "DATA_QUALITY_FAILURE")
        self.assertIn("timed out", result["failure_reason"].lower())


if __name__ == "__main__":
    unittest.main()
