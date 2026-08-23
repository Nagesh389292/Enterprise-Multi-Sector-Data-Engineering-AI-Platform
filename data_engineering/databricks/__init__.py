"""
Databricks Integration Package for Enterprise Data & AI Platform.

Provides cloud execution target capabilities:
  - client.py    : Workspace client, authentication, connectivity
  - health.py    : Warehouse health check, connectivity verification
  - sql.py       : SQL Statement Execution API (async poll)
  - jobs.py      : Jobs API (trigger, monitor, retrieve results)
  - gold_sync.py : Gold data sync and cross-platform reconciliation
"""
from data_engineering.databricks.client import DatabricksClient
from data_engineering.databricks.health import DatabricksHealthChecker

__all__ = ["DatabricksClient", "DatabricksHealthChecker"]
