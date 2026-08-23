"""
Databricks Workspace Client.

Provides authenticated workspace connectivity using the official Databricks SDK.
Supports Personal Access Token (PAT) authentication via environment variables only.

Security rules enforced:
- Token is NEVER logged, printed, or included in exception messages.
- All config is loaded from environment variables; no hardcoded secrets.
- Raises ValueError clearly if required config is missing.

Usage:
    client = DatabricksClient()
    ws = client.workspace_client()
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def _safe_host(host: str) -> str:
    """Returns host URL stripped to safe domain-only form for logging."""
    return host.split("//")[-1].split("/")[0] if host else "<not set>"


class DatabricksConfig:
    """Loads and validates Databricks configuration from environment variables."""

    def __init__(self):
        self.host: str = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
        self.workspace_id: str = os.environ.get("DATABRICKS_WORKSPACE_ID", "")
        self.warehouse_id: str = os.environ.get("DATABRICKS_WAREHOUSE_ID", "")
        self.auth_mode: str = os.environ.get("DATABRICKS_AUTH_MODE", "pat").lower()
        self.catalog: str = os.environ.get("DATABRICKS_CATALOG", "workspace")
        self.schema: str = os.environ.get("DATABRICKS_SCHEMA", "enterprise_gold")
        # Credentials loaded from env — NEVER exposed or logged
        self._token: str = os.environ.get("DATABRICKS_TOKEN", "")
        self._client_id: str = os.environ.get("DATABRICKS_CLIENT_ID", "")
        self._client_secret: str = os.environ.get("DATABRICKS_CLIENT_SECRET", "")

    @property
    def token_present(self) -> bool:
        """Returns True if a PAT or OAuth Client ID/Secret is configured."""
        return bool(self._token or (self._client_id and self._client_secret))

    @property
    def token(self) -> str:
        """Returns the raw token for SDK auth only. Do NOT log this value."""
        return self._token

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret

    @property
    def host_configured(self) -> bool:
        return bool(self.host and self.host.startswith("https://"))

    @property
    def warehouse_configured(self) -> bool:
        return bool(self.warehouse_id)

    def validate(self) -> Dict[str, Any]:
        """Returns validation result dict. Does not raise; caller decides what to do."""
        issues = []
        if not self.host_configured:
            issues.append("DATABRICKS_HOST is not set or invalid (must start with https://)")
        if not self.warehouse_configured:
            issues.append("DATABRICKS_WAREHOUSE_ID is not set")
        if not self.token_present:
            issues.append("Neither DATABRICKS_TOKEN nor DATABRICKS_CLIENT_ID/CLIENT_SECRET is set")
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "host": _safe_host(self.host),
            "warehouse_id": self.warehouse_id or "<not set>",
            "auth_mode": "oauth" if (self._client_id and self._client_secret) else "pat",
            "token_present": self.token_present,
        }

    def require_valid(self) -> None:
        """Raises ValueError with actionable message if configuration is invalid."""
        result = self.validate()
        if not result["valid"]:
            raise ValueError(
                f"Databricks configuration incomplete. Issues:\n"
                + "\n".join(f"  - {i}" for i in result["issues"])
                + "\n\nSet the required environment variables in your local .env file."
                + "\nDo NOT paste tokens or client secrets in source code or chat."
            )


class DatabricksClient:
    """
    Authenticated Databricks Workspace Client.

    Uses the official databricks-sdk WorkspaceClient for all API calls.
    Credentials are loaded from environment only — never from parameters or source code.
    """

    def __init__(self, config: Optional[DatabricksConfig] = None):
        self.config = config or DatabricksConfig()

    def workspace_client(self):
        """
        Returns an authenticated databricks-sdk WorkspaceClient.
        Supports PAT, OAuth M2M (client_id + client_secret), or SDK auto-auth.
        """
        try:
            from databricks.sdk import WorkspaceClient
        except ImportError:
            raise ImportError(
                "databricks-sdk is not installed. "
                "Install it with: pip install databricks-sdk"
            )

        self.config.require_valid()

        if self.config.client_id and self.config.client_secret:
            client = WorkspaceClient(
                host=self.config.host,
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
            )
        elif self.config.token:
            client = WorkspaceClient(
                host=self.config.host,
                token=self.config.token,
            )
        else:
            client = WorkspaceClient(host=self.config.host)

        logger.info(
            "[DatabricksClient] WorkspaceClient initialized for host: %s",
            _safe_host(self.config.host),
        )
        return client

    def get_config_summary(self) -> Dict[str, Any]:
        """Returns a safe configuration summary (no credentials)."""
        v = self.config.validate()
        return {
            "host": v["host"],
            "warehouse_id": v["warehouse_id"],
            "auth_mode": v["auth_mode"],
            "token_present": v["token_present"],
            "catalog": self.config.catalog,
            "schema": self.config.schema,
            "config_valid": v["valid"],
            "config_issues": v["issues"],
        }


if __name__ == "__main__":
    client = DatabricksClient()
    summary = client.get_config_summary()
    print("[DatabricksClient] Configuration Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
