"""
Databricks SQL Statement Execution API.

Uses the Databricks SDK StatementExecutionAPI to execute SQL queries
against a SQL Warehouse with full async polling, timeout handling,
and safe error reporting.

Security: Token never appears in logs or error messages.

Usage:
    executor = DatabricksSQLExecutor()
    result = executor.execute("SELECT 1 AS test")
    print(result)
"""

import time
import logging
from typing import Dict, Any, List, Optional

from data_engineering.databricks.client import DatabricksClient, DatabricksConfig

logger = logging.getLogger(__name__)

# Databricks SQL statement terminal states
TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CANCELED", "CLOSED"}
POLL_INTERVAL_SECS = 1.5
DEFAULT_TIMEOUT_SECS = 60


class DatabricksSQLExecutor:
    """
    Executes SQL statements against a Databricks SQL Warehouse.

    - Uses SDK StatementExecutionAPI (async by default)
    - Polls until terminal state or timeout
    - Returns structured result dict with rows, columns, and metadata
    - Never logs the token or exposes it in errors
    """

    def __init__(
        self,
        config: Optional[DatabricksConfig] = None,
        timeout_secs: int = DEFAULT_TIMEOUT_SECS,
    ):
        self.config = config or DatabricksConfig()
        self.client = DatabricksClient(self.config)
        self.timeout_secs = timeout_secs

    def execute(self, sql: str, timeout_secs: int = None) -> Dict[str, Any]:
        """
        Executes a SQL statement and returns the full result.

        Args:
            sql: SQL statement string (SELECT only for safe use)
            timeout_secs: Override default timeout

        Returns:
            Dict with keys: success, sql, rows, columns, row_count,
                            state, warehouse_id, elapsed_secs, error
        """
        timeout = timeout_secs or self.timeout_secs

        try:
            ws = self.client.workspace_client()
        except (ValueError, ImportError) as e:
            return {
                "success": False,
                "sql": sql,
                "rows": [],
                "columns": [],
                "row_count": 0,
                "state": "NOT_EXECUTED",
                "error": str(e),
                "elapsed_secs": 0.0,
            }

        start = time.time()
        try:
            # Submit statement
            logger.info("[DatabricksSQL] Submitting statement to warehouse %s", self.config.warehouse_id)
            response = ws.statement_execution.execute_statement(
                statement=sql,
                warehouse_id=self.config.warehouse_id,
            )
            statement_id = response.statement_id
            logger.info("[DatabricksSQL] Statement submitted: id=%s", statement_id)

            # Poll until terminal state
            while True:
                elapsed = time.time() - start
                if elapsed > timeout:
                    logger.warning("[DatabricksSQL] Timeout after %.1fs for statement %s", elapsed, statement_id)
                    try:
                        ws.statement_execution.cancel_execution(statement_id=statement_id)
                    except Exception:
                        pass
                    return {
                        "success": False,
                        "sql": sql,
                        "rows": [],
                        "columns": [],
                        "row_count": 0,
                        "state": "TIMEOUT",
                        "statement_id": statement_id,
                        "error": f"Query timed out after {timeout}s",
                        "elapsed_secs": round(elapsed, 2),
                    }

                status_response = ws.statement_execution.get_statement(statement_id=statement_id)
                raw_state = getattr(getattr(status_response, "status", None), "state", "UNKNOWN")
                state_val = getattr(raw_state, "value", str(raw_state))
                state = str(state_val).upper()
                logger.debug("[DatabricksSQL] Poll state=%s elapsed=%.1fs", state, elapsed)

                if state in TERMINAL_STATES:
                    break

                time.sleep(POLL_INTERVAL_SECS)

            elapsed = round(time.time() - start, 2)

            if state != "SUCCEEDED":
                error_msg = ""
                try:
                    error_msg = str(status_response.status.error.message)
                except Exception:
                    error_msg = f"Statement ended with state: {state}"
                return {
                    "success": False,
                    "sql": sql,
                    "rows": [],
                    "columns": [],
                    "row_count": 0,
                    "state": state,
                    "statement_id": statement_id,
                    "error": error_msg,
                    "elapsed_secs": elapsed,
                }

            # Extract results
            columns, rows = self._extract_results(status_response)
            logger.info("[DatabricksSQL] Statement SUCCEEDED: %d rows in %.2fs", len(rows), elapsed)

            return {
                "success": True,
                "sql": sql,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "state": "SUCCEEDED",
                "statement_id": statement_id,
                "warehouse_id": self.config.warehouse_id,
                "catalog": self.config.catalog,
                "elapsed_secs": elapsed,
                "error": None,
            }

        except Exception as e:
            elapsed = round(time.time() - start, 2)
            safe_err = str(e)
            if self.config.token:
                safe_err = safe_err.replace(self.config.token, "<REDACTED>")
            if self.config.client_secret:
                safe_err = safe_err.replace(self.config.client_secret, "<REDACTED>")
            return {
                "success": False,
                "sql": sql,
                "rows": [],
                "columns": [],
                "row_count": 0,
                "state": "ERROR",
                "error": safe_err[:500],
                "elapsed_secs": elapsed,
            }

    def _extract_results(self, response) -> tuple:
        """Extracts column names and row data from a successful statement response."""
        try:
            schema = response.manifest.schema
            columns = [col.name for col in schema.columns] if schema and schema.columns else []
        except Exception:
            columns = []

        rows = []
        try:
            result = response.result
            if result and result.data_array:
                for raw_row in result.data_array:
                    if columns:
                        rows.append(dict(zip(columns, raw_row)))
                    else:
                        rows.append(list(raw_row))
        except Exception as e:
            logger.warning("[DatabricksSQL] Could not extract result rows: %s", e)

        return columns, rows

    def execute_connection_test(self) -> Dict[str, Any]:
        """Executes the standard connectivity verification query."""
        return self.execute("SELECT 1 AS databricks_connection_test")

    def execute_catalog_context(self) -> Dict[str, Any]:
        """Executes the catalog/schema/user context query."""
        return self.execute(
            "SELECT current_catalog() AS catalog, "
            "current_schema() AS schema, "
            "current_user() AS user"
        )

    def execute_gold_summary_query(self) -> Dict[str, Any]:
        """Queries the Gold multi-sector summary table from Databricks."""
        sql = (
            f"SELECT sector, total_records, primary_metric, primary_metric_value, "
            f"secondary_metric, secondary_metric_value, updated_at "
            f"FROM {self.config.catalog}.{self.config.schema}.gold_multi_sector_summary "
            f"ORDER BY sector"
        )
        return self.execute(sql)


if __name__ == "__main__":
    executor = DatabricksSQLExecutor()
    print("[DatabricksSQL] Running connection test...")
    result = executor.execute_connection_test()
    print(f"  success: {result['success']}")
    print(f"  rows:    {result['rows']}")
    print(f"  elapsed: {result['elapsed_secs']}s")
