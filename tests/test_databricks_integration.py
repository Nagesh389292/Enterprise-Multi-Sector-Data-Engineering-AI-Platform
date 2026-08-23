"""
Databricks Integration Unit Tests.

All 10 tests use mocking — no real cloud calls are made.
These tests verify:
  1. Configuration validation
  2. Missing credential handling
  3. Invalid host handling
  4. Warehouse STOPPED handling
  5. Timeout handling
  6. Authentication failure handling
  7. SQL response parsing
  8. Gold reconciliation logic
  9. No-secret logging assertion
 10. Local fallback behavior

To test REAL runtime connectivity, run:
    python scripts/verify_databricks_runtime.py

NEVER label mocked tests as runtime verification.
"""

import os
import json
import logging
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDatabricksIntegration(unittest.TestCase):
    """Mocked unit tests for Databricks integration components."""

    # ---------------------------------------------------------------
    # 1. Configuration validation — all vars present
    # ---------------------------------------------------------------
    def test_01_config_validation_complete(self):
        """Config validates successfully when all required vars are present."""
        env = {
            "DATABRICKS_HOST": "https://dbc-988b03b0-c952.cloud.databricks.com",
            "DATABRICKS_WAREHOUSE_ID": "1f1403d78bfa0404",
            "DATABRICKS_TOKEN": "dapi_test_token_placeholder",
            "DATABRICKS_CATALOG": "workspace",
            "DATABRICKS_SCHEMA": "enterprise_gold",
        }
        with patch.dict(os.environ, env, clear=False):
            from data_engineering.databricks.client import DatabricksConfig
            config = DatabricksConfig()
            result = config.validate()
            self.assertTrue(result["valid"], f"Expected valid config but got: {result['issues']}")
            self.assertTrue(result["token_present"])
            self.assertEqual(result["host"], "dbc-988b03b0-c952.cloud.databricks.com")

    # ---------------------------------------------------------------
    # 2. Missing DATABRICKS_TOKEN raises ValueError
    # ---------------------------------------------------------------
    def test_02_missing_token_raises_value_error(self):
        """Missing DATABRICKS_TOKEN causes require_valid() to raise ValueError."""
        env = {
            "DATABRICKS_HOST": "https://dbc-988b03b0-c952.cloud.databricks.com",
            "DATABRICKS_WAREHOUSE_ID": "1f1403d78bfa0404",
        }
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("DATABRICKS_TOKEN", None)
            os.environ.pop("DATABRICKS_CLIENT_ID", None)
            os.environ.pop("DATABRICKS_CLIENT_SECRET", None)
            from data_engineering.databricks.client import DatabricksConfig
            config = DatabricksConfig()
            with self.assertRaises(ValueError) as ctx:
                config.require_valid()
            self.assertIn("DATABRICKS_TOKEN", str(ctx.exception))
            # Token must not appear in the error (it's blank in this test, but check structure)
            self.assertNotIn("dapi", str(ctx.exception).lower())

    # ---------------------------------------------------------------
    # 3. Invalid host raises ValueError
    # ---------------------------------------------------------------
    def test_03_invalid_host_raises_value_error(self):
        """Non-https host causes require_valid() to raise ValueError."""
        env = {
            "DATABRICKS_HOST": "http://not-secure.databricks.com",
            "DATABRICKS_WAREHOUSE_ID": "1f1403d78bfa0404",
            "DATABRICKS_TOKEN": "dapi_test_token_placeholder",
        }
        with patch.dict(os.environ, env, clear=False):
            from importlib import reload
            import data_engineering.databricks.client as client_mod
            reload(client_mod)
            config = client_mod.DatabricksConfig()
            # http:// host is not valid (must be https://)
            self.assertFalse(config.host_configured)
            with self.assertRaises(ValueError):
                config.require_valid()

    # ---------------------------------------------------------------
    # 4. Warehouse STOPPED → health report shows STOPPED, no auto-start
    # ---------------------------------------------------------------
    def test_04_warehouse_stopped_no_auto_start(self):
        """Health check reports STOPPED state and never attempts to start the warehouse."""
        env = {
            "DATABRICKS_HOST": "https://dbc-988b03b0-c952.cloud.databricks.com",
            "DATABRICKS_WAREHOUSE_ID": "1f1403d78bfa0404",
            "DATABRICKS_TOKEN": "dapi_test_token_placeholder",
        }
        with patch.dict(os.environ, env, clear=False):
            from data_engineering.databricks.health import DatabricksHealthChecker

            mock_ws = MagicMock()
            mock_warehouse = MagicMock()
            mock_warehouse.state = MagicMock()
            mock_warehouse.state.__str__ = lambda _: "STOPPED"
            mock_warehouse.name = "enterprise-warehouse"
            mock_warehouse.cluster_size = "Small"
            mock_warehouse.auto_stop_mins = 10
            mock_ws.warehouses.get.return_value = mock_warehouse
            mock_ws.current_user.me.return_value = MagicMock(user_name="test@example.com", display_name="Test User")

            checker = DatabricksHealthChecker()
            with patch.object(checker.client, "workspace_client", return_value=mock_ws):
                result = checker.check_warehouse_state()

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["warehouse_state"], "STOPPED")
            # Verify start() was never called
            mock_ws.warehouses.start.assert_not_called()

    # ---------------------------------------------------------------
    # 5. Timeout handling
    # ---------------------------------------------------------------
    def test_05_sql_timeout_handling(self):
        """SQL executor returns TIMEOUT state when query exceeds timeout."""
        env = {
            "DATABRICKS_HOST": "https://dbc-988b03b0-c952.cloud.databricks.com",
            "DATABRICKS_WAREHOUSE_ID": "1f1403d78bfa0404",
            "DATABRICKS_TOKEN": "dapi_test_token_placeholder",
        }
        with patch.dict(os.environ, env, clear=False):
            from data_engineering.databricks.sql import DatabricksSQLExecutor

            mock_ws = MagicMock()
            mock_response = MagicMock()
            mock_response.statement_id = "stmt-001"
            mock_ws.statement_execution.execute_statement.return_value = mock_response

            # Return non-terminal state indefinitely (simulates hanging query)
            mock_status = MagicMock()
            mock_status.status.state = MagicMock()
            mock_status.status.state.__str__ = lambda _: "RUNNING"
            mock_ws.statement_execution.get_statement.return_value = mock_status

            executor = DatabricksSQLExecutor(timeout_secs=1)  # Very short timeout
            with patch.object(executor.client, "workspace_client", return_value=mock_ws):
                result = executor.execute("SELECT sleep(999)")

            self.assertFalse(result["success"])
            self.assertEqual(result["state"], "TIMEOUT")
            self.assertIn("timed out", result["error"].lower())

    # ---------------------------------------------------------------
    # 6. Authentication failure — no credential leak
    # ---------------------------------------------------------------
    def test_06_auth_failure_no_credential_leak(self):
        """Authentication failure is reported safely without leaking the token."""
        secret_token = "dapi_super_secret_real_token_12345"
        env = {
            "DATABRICKS_HOST": "https://dbc-988b03b0-c952.cloud.databricks.com",
            "DATABRICKS_WAREHOUSE_ID": "1f1403d78bfa0404",
            "DATABRICKS_TOKEN": secret_token,
        }
        with patch.dict(os.environ, env, clear=False):
            from data_engineering.databricks.health import DatabricksHealthChecker

            mock_ws = MagicMock()
            mock_ws.current_user.me.side_effect = Exception(
                f"HTTP 401: Unauthorized — invalid token {secret_token}"
            )

            checker = DatabricksHealthChecker()
            with patch.object(checker.client, "workspace_client", return_value=mock_ws):
                result = checker.check_authentication()

            self.assertEqual(result["status"], "FAIL")
            detail = result.get("detail", "")
            self.assertNotIn(secret_token, detail, "Token must not appear in error output")

    # ---------------------------------------------------------------
    # 7. SQL response parsing — success path
    # ---------------------------------------------------------------
    def test_07_sql_response_parsing(self):
        """SQL executor correctly parses row/column results from SDK response."""
        env = {
            "DATABRICKS_HOST": "https://dbc-988b03b0-c952.cloud.databricks.com",
            "DATABRICKS_WAREHOUSE_ID": "1f1403d78bfa0404",
            "DATABRICKS_TOKEN": "dapi_test_token_placeholder",
        }
        with patch.dict(os.environ, env, clear=False):
            from data_engineering.databricks.sql import DatabricksSQLExecutor

            mock_ws = MagicMock()

            # Submit returns statement_id
            mock_submit = MagicMock()
            mock_submit.statement_id = "stmt-002"
            mock_ws.statement_execution.execute_statement.return_value = mock_submit

            # Poll returns SUCCEEDED
            mock_col = MagicMock()
            mock_col.name = "databricks_connection_test"
            mock_state = MagicMock()
            mock_state.__str__ = lambda s: "SUCCEEDED"
            mock_state.value = "SUCCEEDED"
            mock_status = MagicMock()
            mock_status.status.state = mock_state
            mock_status.manifest.schema.columns = [mock_col]
            mock_status.result.data_array = [["1"]]
            mock_ws.statement_execution.get_statement.return_value = mock_status

            executor = DatabricksSQLExecutor()
            with patch.object(executor.client, "workspace_client", return_value=mock_ws):
                result = executor.execute("SELECT 1 AS databricks_connection_test")

            self.assertTrue(result["success"])
            self.assertEqual(result["state"], "SUCCEEDED")
            self.assertEqual(len(result["rows"]), 1)
            self.assertIn("databricks_connection_test", result["columns"])

    # ---------------------------------------------------------------
    # 8. Gold reconciliation — matching values pass
    # ---------------------------------------------------------------
    def test_08_gold_reconciliation_matching_values(self):
        """Reconciliation passes when Databricks Gold matches local canonical values."""
        env = {
            "DATABRICKS_HOST": "https://dbc-988b03b0-c952.cloud.databricks.com",
            "DATABRICKS_WAREHOUSE_ID": "1f1403d78bfa0404",
            "DATABRICKS_TOKEN": "dapi_test_token_placeholder",
        }
        with patch.dict(os.environ, env, clear=False):
            from data_engineering.databricks.gold_sync import DatabricksGoldSync

            syncer = DatabricksGoldSync()

            # Mock the SQL query to return the same values as canonical Gold
            mock_db_result = {
                "success": True,
                "rows": [
                    {"sector": "Credit Card Fraud",       "primary_metric_value": 11.04},
                    {"sector": "Banking Loan Risk",        "primary_metric_value": 65.5},
                    {"sector": "Healthcare OGD",           "primary_metric_value": 76.48},
                    {"sector": "Clinical EHR Readmission", "primary_metric_value": 25.25},
                    {"sector": "Insurance Claims Fraud",   "primary_metric_value": 20.0},
                    {"sector": "Retail Sales & Demand",    "primary_metric_value": 32277430.52},
                ],
            }

            with patch.object(syncer.executor, "execute_gold_summary_query", return_value=mock_db_result):
                result = syncer.reconcile_gold_metrics()

            self.assertTrue(result["success"], f"Reconciliation failed: {result['mismatches']}")
            self.assertEqual(result["sectors_mismatched"], 0)
            self.assertEqual(result["sectors_matched"], 6)

    # ---------------------------------------------------------------
    # 9. No-secret logging
    # ---------------------------------------------------------------
    def test_09_no_secret_in_logs(self):
        """Confirm that token never appears in log output during operations."""
        secret_token = "dapi_never_log_this_token_xyz789"
        env = {
            "DATABRICKS_HOST": "https://dbc-988b03b0-c952.cloud.databricks.com",
            "DATABRICKS_WAREHOUSE_ID": "1f1403d78bfa0404",
            "DATABRICKS_TOKEN": secret_token,
        }
        with patch.dict(os.environ, env, clear=False):
            import io
            from data_engineering.databricks.client import DatabricksConfig

            # Capture log output
            log_stream = io.StringIO()
            handler = logging.StreamHandler(log_stream)
            handler.setLevel(logging.DEBUG)
            root_logger = logging.getLogger("data_engineering.databricks")
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.DEBUG)

            try:
                config = DatabricksConfig()
                summary = config.validate()
                # Config summary must not contain the token
                summary_str = json.dumps(summary)
                self.assertNotIn(secret_token, summary_str)
                # Log output must not contain the token
                log_output = log_stream.getvalue()
                self.assertNotIn(secret_token, log_output)
            finally:
                root_logger.removeHandler(handler)

    # ---------------------------------------------------------------
    # 10. Local fallback — no Databricks env → graceful degradation
    # ---------------------------------------------------------------
    def test_10_local_fallback_no_databricks_env(self):
        """When no Databricks env vars are set, config validation fails gracefully (no crash)."""
        # Clear all Databricks env vars
        clear_env = {
            "DATABRICKS_HOST": "",
            "DATABRICKS_WAREHOUSE_ID": "",
            "DATABRICKS_TOKEN": "",
        }
        with patch.dict(os.environ, clear_env, clear=False):
            from importlib import reload
            import data_engineering.databricks.client as client_mod
            reload(client_mod)

            config = client_mod.DatabricksConfig()
            result = config.validate()

            # Must return a dict with valid=False and actionable issues
            self.assertFalse(result["valid"])
            self.assertTrue(len(result["issues"]) > 0)
            # Must NOT raise an unhandled exception — graceful degradation
            # The platform should continue working locally when Databricks is not configured

    # Explicit labels
    TEST_CATEGORIES = {
        "test_01": "configuration_validation",
        "test_02": "missing_credential_handling",
        "test_03": "invalid_host_handling",
        "test_04": "warehouse_stopped_handling",
        "test_05": "timeout_handling",
        "test_06": "authentication_failure_no_leak",
        "test_07": "sql_response_parsing",
        "test_08": "gold_reconciliation_logic",
        "test_09": "no_secret_logging",
        "test_10": "local_fallback_behavior",
    }


if __name__ == "__main__":
    unittest.main(verbosity=2)
