# Snowflake Analytical Warehouse — Architectural Integration Plan

> **Status**: PLANNED / OPTIONAL  
> **Account URL**: `https://ohjblgo-yf62059.snowflakecomputing.com`  
> **Policy**: Optional architecture plan. No credentials or active deployment until access is explicitly verified.

---

## 1. Target Architecture

```text
               Databricks Lakehouse
                        │
                  Delta / Gold
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
     Databricks SQL       Snowflake Enterprise
       Warehouse               Warehouse
             │                     │
             └──────────┬──────────┘
                        ▼
                       dbt
                        │
                        ▼
                Analytical Marts
                        │
                ┌───────┴───────┐
                ▼               ▼
          BI Dashboards     AI Copilot
```

---

## 2. Role Distinction: Databricks vs Snowflake

| Capability | Databricks | Snowflake |
| :--- | :--- | :--- |
| **Primary Workload** | Data Engineering, ML/MLOps, PySpark ETL, Delta Lake | Enterprise Data Warehouse, Financial Reporting, Ad-hoc SQL BI |
| **Storage Layer** | DBFS / S3 / GCS (Delta Lake format) | Snowflake Internal / External Stage (Micro-partitions) |
| **ETL / Compute** | PySpark + Databricks Workflows | Snowpipe + dbt SQL Transformations |
| **Governance** | Unity Catalog | Snowflake RBAC / Data Clean Rooms |

---

## 3. Downstream Snowflake Ingestion Architecture

If Snowflake access is enabled in the future, the ingestion pipeline from Databricks Gold to Snowflake will follow this pattern:

1. **Storage Integration**:
   Configure Snowflake Storage Integration to read directly from GCS/S3 Delta Lake Gold buckets produced by PySpark/Databricks.

2. **External Table / Snowpipe**:
   ```sql
   CREATE OR REPLACE STAGE gold_delta_stage
     URL='gcs://enterprise-gold-bucket/'
     STORAGE_INTEGRATION = gcp_gold_integration;

   CREATE OR REPLACE EXTERNAL TABLE snowflake_dw.public.ext_gold_multi_sector
     LIKE enterprise_platform.gold_schema
     LOCATION=@gold_delta_stage
     FILE_FORMAT = (TYPE = PARQUET);
   ```

3. **dbt Transformation**:
   dbt runs against Snowflake target in `dbt/profiles.yml`:
   ```bash
   dbt run --target prod
   dbt test --target prod
   ```

---

## 4. Cost Control & Safety Measures

- **Warehouse Auto-Suspend**: Set to 60 seconds of inactivity on `COMPUTE_WH`.
- **Resource Monitors**: Set monthly credit quota to prevent runaway billing.
- **Local Fallback**: Local pipeline uses DuckDB (`snowflake_warehouse.duckdb`) for dbt testing when Snowflake credentials are absent.
