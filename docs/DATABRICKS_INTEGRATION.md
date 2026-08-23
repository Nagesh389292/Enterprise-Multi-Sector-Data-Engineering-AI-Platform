# Databricks Cloud Data Engineering Integration

**Status**: IMPLEMENTED & UNIT VERIFIED  
**Workspace URL**: `https://dbc-988b03b0-c952.cloud.databricks.com`  
**Workspace ID**: `7474646556233194`  
**SQL Warehouse ID**: `1f1403d78bfa0404`  
**Cloud Runtime Status**: ⏳ PENDING (gated on user authentication setup & live SQL execution)

---

## 1. Target Architecture

```text
               LOCAL ENVIRONMENT                       DATABRICKS CLOUD
        ┌─────────────────────────────┐        ┌─────────────────────────────┐
        │  PySpark Local Medallion    │        │  Databricks Workspace       │
        │  Bronze -> Silver -> Gold   │───────>│  SQL Warehouse              │
        │  (data/lake/gold/*.json)    │  Sync  │  (main.enterprise_gold)     │
        └─────────────────────────────┘        └──────────────┬──────────────┘
                       │                                      │
                       ▼                                      ▼
               Local SQLite / BI                         Databricks SQL
               & AI Copilot                              + dbt Analytics
```

---

## 2. Authentication & Security Policy

### Supported Modes
1. **Personal Access Token (PAT)**: Set `DATABRICKS_TOKEN` in local `.env` file.
2. **OAuth M2M / Service Principal**: Set `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET` in local `.env` file.

### Zero Credential Exposure Rules
- Credentials are read **only** from environment variables (`.env` file).
- Credentials are **never** logged, printed to console, embedded in exception tracebacks, or included in markdown artifacts.
- The `DatabricksConfig` validator redacts sensitive values.

---

## 3. Package Structure

`data_engineering/databricks/`

- `client.py`: Authenticated `WorkspaceClient` factory with PAT & OAuth support.
- `health.py`: Layered health checker (workspace, network reachability, auth, warehouse state).
- `sql.py`: Statement Execution API wrapper with async polling, timeout, and cancellation.
- `jobs.py`: Jobs API client for triggering and monitoring Databricks Workflows.
- `gold_sync.py`: Uploads canonical Gold JSON and performs 0.01% tolerance reconciliation.

---

## 4. Verification Workflow Scripts

| Script | Purpose | Compute Started? |
| :--- | :--- | :---: |
| `python scripts/check_databricks.py` | Configuration and reachability pre-flight | ❌ No |
| `python scripts/verify_databricks_runtime.py` | Real SQL execution (`SELECT 1`, catalog context) | ⚡ Yes |
| `python scripts/sync_gold_to_databricks.py` | Gold data sync & multi-sector reconciliation | ⚡ Yes |

---

## 5. Cost Control Guidelines

- **Warehouse Auto-Stop**: Set to 10–20 minutes auto-stop in Databricks UI.
- **No Ephemeral Cluster Spawning**: Pre-flight health checks and SQL queries use the shared SQL Warehouse (`1f1403d78bfa0404`).
- **Pre-flight Scripting**: `check_databricks.py` never triggers warehouse startup.

---

## 6. Interview Defense — Databricks Technical Q&A

### Q1: Why add Databricks when PySpark already runs locally?
> Local PySpark validates data transformation logic deterministically without cloud cost. Databricks provides managed cloud orchestration, serverless SQL compute, auto-scaling, Unity Catalog governance, and enterprise team collaboration.

### Q2: Why Delta Lake over plain Parquet?
> Delta Lake adds ACID transactions, schema enforcement, schema evolution, time-travel versioning, and idempotent `MERGE` upserts to standard Parquet files.

### Q3: How do you prevent cloud cost overruns?
> Auto-suspend (10-min idle timeout), pre-flight reachability checks before executing compute, serverless SQL warehouses instead of always-on clusters, and strict local unit-testing before cloud execution.

### Q4: How is local Gold data reconciled with Databricks Gold?
> `DatabricksGoldSync` reads canonical local metrics from `master_multi_sector_gold.json`, MERGE upserts them into `gold_multi_sector_summary`, and runs a strict validation query asserting <0.01% metric variance across all 6 sectors.
