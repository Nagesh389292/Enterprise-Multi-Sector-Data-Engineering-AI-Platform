"""
Databricks Health Checker.

Provides clear, layered health checks:
  1. Workspace configured (host + token present in env)
  2. Workspace reachable (HTTP connectivity)
  3. Authentication (SDK token validation)
  4. Warehouse configured (ID present)
  5. Warehouse state (RUNNING / STOPPED / UNKNOWN)
  6. SQL execution (NOT TESTED by default — use verify_databricks_runtime.py)

IMPORTANT:
- Does NOT start the warehouse.
- Does NOT expose credentials in output.
- Returns structured dict for programmatic use and human-readable report for CLI.
"""

import os
import logging
import requests
from typing import Dict, Any

from data_engineering.databricks.client import DatabricksClient, DatabricksConfig, _safe_host

logger = logging.getLogger(__name__)

HEALTH_PASS = "PASS"
HEALTH_FAIL = "FAIL"
HEALTH_NOT_CONFIGURED = "NOT_CONFIGURED"
HEALTH_NOT_TESTED = "NOT_TESTED"
HEALTH_UNKNOWN = "UNKNOWN"


class DatabricksHealthChecker:
    """
    Runs structured health checks against the Databricks workspace.
    Never starts compute. Never exposes credentials.
    """

    def __init__(self, config: DatabricksConfig = None):
        self.config = config or DatabricksConfig()
        self.client = DatabricksClient(self.config)

    def check_workspace_configured(self) -> Dict[str, Any]:
        """Validates that host and token are present in environment."""
        v = self.config.validate()
        if not self.config.host_configured:
            return {
                "status": HEALTH_NOT_CONFIGURED,
                "detail": "DATABRICKS_HOST not set or not an https:// URL",
            }
        if not self.config.token_present:
            return {
                "status": HEALTH_NOT_CONFIGURED,
                "detail": "Neither DATABRICKS_TOKEN nor DATABRICKS_CLIENT_ID/CLIENT_SECRET set in environment",
            }
        return {
            "status": HEALTH_PASS if v["valid"] else HEALTH_FAIL,
            "host": v["host"],
            "auth_mode": v["auth_mode"],
            "detail": "Configuration complete" if v["valid"] else "; ".join(v["issues"]),
        }

    def check_workspace_reachable(self, timeout: int = 5) -> Dict[str, Any]:
        """Tests network reachability of the Databricks workspace host."""
        if not self.config.host_configured:
            return {"status": HEALTH_NOT_CONFIGURED, "detail": "Host not configured"}
        try:
            # Public endpoint — no auth required to test reachability
            url = f"{self.config.host}/api/2.0/clusters/spark-versions"
            resp = requests.get(url, timeout=timeout)
            # 401 = reachable but unauthenticated (expected without token in this check)
            if resp.status_code in (200, 401, 403):
                return {
                    "status": HEALTH_PASS,
                    "host": _safe_host(self.config.host),
                    "http_status": resp.status_code,
                    "detail": "Host reachable",
                }
            return {
                "status": HEALTH_FAIL,
                "host": _safe_host(self.config.host),
                "http_status": resp.status_code,
                "detail": f"Unexpected HTTP status: {resp.status_code}",
            }
        except requests.Timeout:
            return {
                "status": HEALTH_FAIL,
                "detail": f"Connection timed out after {timeout}s",
            }
        except requests.ConnectionError as e:
            return {
                "status": HEALTH_FAIL,
                "detail": f"Connection error: {type(e).__name__}",
            }

    def check_authentication(self) -> Dict[str, Any]:
        """Validates authentication using the Databricks SDK current_user API."""
        if not self.config.token_present:
            return {"status": HEALTH_NOT_CONFIGURED, "detail": "DATABRICKS_TOKEN not set"}
        if not self.config.host_configured:
            return {"status": HEALTH_NOT_CONFIGURED, "detail": "DATABRICKS_HOST not set"}
        try:
            ws = self.client.workspace_client()
            user = ws.current_user.me()
            return {
                "status": HEALTH_PASS,
                "user_name": getattr(user, "user_name", "unknown"),
                "display_name": getattr(user, "display_name", ""),
                "detail": "Authentication successful",
            }
        except Exception as e:
            err_type = type(e).__name__
            # Never include token in error message
            safe_msg = str(e).replace(self.config.token, "<REDACTED>") if self.config.token_present else str(e)
            return {
                "status": HEALTH_FAIL,
                "error_type": err_type,
                "detail": f"Authentication failed: {err_type} — {safe_msg[:200]}",
            }

    def check_warehouse_state(self) -> Dict[str, Any]:
        """Retrieves the current state of the SQL Warehouse. Never starts it."""
        if not self.config.warehouse_configured:
            return {"status": HEALTH_NOT_CONFIGURED, "detail": "DATABRICKS_WAREHOUSE_ID not set"}
        if not self.config.token_present:
            return {"status": HEALTH_NOT_CONFIGURED, "detail": "DATABRICKS_TOKEN not set"}
        try:
            ws = self.client.workspace_client()
            warehouse = ws.warehouses.get(self.config.warehouse_id)
            state = str(getattr(warehouse, "state", "UNKNOWN")).upper()
            # Normalize SDK state enum to string
            if "RUNNING" in state:
                state_str = "RUNNING"
            elif "STOPPED" in state or "DELETED" in state:
                state_str = "STOPPED"
            elif "STARTING" in state:
                state_str = "STARTING"
            else:
                state_str = state
            return {
                "status": HEALTH_PASS,
                "warehouse_id": self.config.warehouse_id,
                "warehouse_name": getattr(warehouse, "name", "unknown"),
                "warehouse_state": state_str,
                "warehouse_size": getattr(warehouse, "cluster_size", "unknown"),
                "auto_stop_mins": getattr(warehouse, "auto_stop_mins", "unknown"),
                "detail": f"Warehouse state: {state_str}",
            }
        except Exception as e:
            err_type = type(e).__name__
            safe_msg = str(e).replace(self.config.token, "<REDACTED>") if self.config.token_present else str(e)
            return {
                "status": HEALTH_FAIL,
                "error_type": err_type,
                "detail": f"Warehouse check failed: {err_type} — {safe_msg[:200]}",
            }

    def get_health_report(self) -> Dict[str, Any]:
        """
        Runs all health checks and returns a structured report.
        SQL execution is not tested here — use verify_databricks_runtime.py.
        """
        configured = self.check_workspace_configured()
        reachable = self.check_workspace_reachable()
        auth = self.check_authentication()
        warehouse = self.check_warehouse_state()

        all_pass = all(
            r["status"] == HEALTH_PASS
            for r in [configured, reachable, auth, warehouse]
        )

        return {
            "workspace_configured": configured,
            "workspace_reachable": reachable,
            "authentication": auth,
            "warehouse_configured": {
                "status": HEALTH_PASS if self.config.warehouse_configured else HEALTH_NOT_CONFIGURED,
                "warehouse_id": self.config.warehouse_id or "<not set>",
            },
            "warehouse_state": warehouse,
            "sql_execution": {
                "status": HEALTH_NOT_TESTED,
                "detail": "Run scripts/verify_databricks_runtime.py for real SQL verification",
            },
            "overall": HEALTH_PASS if all_pass else HEALTH_FAIL,
        }

    def print_report(self) -> None:
        """Prints a human-readable health report to stdout (no credentials)."""
        report = self.get_health_report()

        def fmt(label: str, check: Dict) -> str:
            status = check.get("status", HEALTH_UNKNOWN)
            badge = "[PASS]" if status == HEALTH_PASS else ("[WARN]" if status == HEALTH_NOT_CONFIGURED else ("[SKIP]" if status == HEALTH_NOT_TESTED else "[FAIL]"))
            detail = check.get("detail", check.get("warehouse_state", check.get("warehouse_id", "")))
            return f"  {badge:<8} {label:<35} {status:<20} {detail}"

        print("\n" + "=" * 75)
        print("  DATABRICKS PLATFORM HEALTH CHECK")
        print("=" * 75)
        print(fmt("Workspace configured", report["workspace_configured"]))
        print(fmt("Workspace reachable", report["workspace_reachable"]))
        print(fmt("Authentication", report["authentication"]))
        print(fmt("Warehouse configured", report["warehouse_configured"]))
        print(fmt("Warehouse state", report["warehouse_state"]))
        print(fmt("SQL execution", report["sql_execution"]))
        print("-" * 75)
        overall = report["overall"]
        badge = "[PASS]" if overall == HEALTH_PASS else "[FAIL]"
        print(f"  {badge:<8} Overall: {overall}")
        print("=" * 75 + "\n")


if __name__ == "__main__":
    checker = DatabricksHealthChecker()
    checker.print_report()
