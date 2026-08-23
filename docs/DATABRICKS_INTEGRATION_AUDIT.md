# docs/DATABRICKS_INTEGRATION_AUDIT.md

# Databricks Integration Pre-Implementation Audit

**Audit Date**: 2026-08-23  
**Auditor**: Senior Data Engineering Lead  
**Databricks Workspace**: `https://dbc-988b03b0-c952.cloud.databricks.com`  
**Workspace ID**: `7474646556233194`  
**SQL Warehouse ID**: `1f1403d78bfa0404`  
**Warehouse Status at audit time**: RUNNING (user confirmed)  
**Platform Status**: Release Candidate (RC) — 55/55 tests, PAT-04 conditional, PAT-05 passed

---

## 1. Current PySpark Pipeline Entry Points

| Entry Point | Path | Role |
| :--- | :--- | :--- |
| Spark session factory | `data_engineering/spark/spark_session.py` | `get_spark_session()` — local `master("local[*]")` hardcoded |
| Bronze ingestion | `data_engineering/spark/bronze.py` | `SparkBronzeIngestion` — credit card Parquet |
| Silver validation | `data_engineering/spark/silver.py` | `SparkSilverProcessor` — feature engineering |
| Gold aggregation | `data_engineering/spark/gold.py` | `SparkGoldAggregation` — 4 credit-card Gold marts |
| Multi-sector pipeline | `data_engineering/spark/multi_sector_pipeline.py` | `MultiSectorSparkPipeline.run_all_pipelines()` — **authoritative 6-sector Gold producer** |
| Medallion pipeline | `data_engineering/spark/medallion_pipeline.py` | End-to-end orchestration wrapper |
| CDC ingestion | `data_engineering/spark/incremental_cdc.py` | Watermark-based incremental micro-batch |
| Local Delta engine | `data_engineering/databricks_delta.py` | `DatabricksDeltaEngine` — local only, Delta JAR fallback |

**Key finding**: `spark_session.py` uses `local[*]` only. No remote cluster target exists yet.

---

## 2. Bronze / Silver / Gold Implementation

### Bronze
- **Storage**: Parquet files at `data/lake/bronze/{sector}/data.parquet`
- **Engine**: PyArrow (primary) / PySpark (when available)
- **Format**: Partitioned by `year`, `month` for credit card; flat Parquet for multi-sector
- **Sectors covered**: credit_card, banking, healthcare, clinical, insurance, retail

### Silver
- **Storage**: Parquet files at `data/lake/silver/{sector}/data.parquet`
- **Transformations**: deduplication, `amount_zscore`, feature engineering, type casting

### Gold
- **Primary output**: `data/lake/gold/master_multi_sector_gold.json` ← **canonical source of truth**
- **Per-sector Gold**: `data/lake/gold/gold_{sector}/data.parquet`
- **Credit-card specific**: `gold_fraud_metrics`, `gold_customer_risk`, `gold_merchant_risk`, `gold_daily_transactions`
- **SQL sync**: `data_engineering/postgres_sync.py → PostgresGoldSync.sync_all_marts()` → `gold_multi_sector_summary` table (PostgreSQL primary / SQLite fallback)

### Canonical Gold Metrics (from `master_multi_sector_gold.json`, verified live)

| Sector | Key Metric | Value |
| :--- | :--- | :--- |
| Credit Card | `fraud_rate_pct` | **11.04** |
| Credit Card | `total_transactions` | **2,500** |
| Credit Card | `total_volume_usd` | **525,198.22** |
| Banking | `default_rate_pct` | **65.5** |
| Banking | `total_loans` | **1,800** |
| Healthcare | `avg_bed_occupancy_pct` | **76.48** |
| Healthcare | `total_hospitals_reporting` | **1,200** |
| Clinical | `readmission_rate_pct` | **25.25** |
| Clinical | `total_patients_analyzed` | **2,000** |
| Insurance | `claims_fraud_rate_pct` | **20.0** |
| Insurance | `total_claims_processed` | **1,500** |
| Retail | `gross_revenue_usd` | **32,277,430.52** |
| Retail | `total_invoices` | **3,000** |

**These values are the reconciliation reference for Databricks Gold validation.**

---

## 3. Existing Delta / Parquet Logic

| Component | Location | Status |
| :--- | :--- | :--- |
| Delta Engine class | `data_engineering/databricks_delta.py` | Exists — local only, uses `delta-spark` JAR (fallback to Parquet) |
| Delta JAR support | `delta` package | ⚠️ Installed but `delta.configure_spark_with_delta` fails at runtime — falls back silently to Parquet |
| Delta write method | `DatabricksDeltaEngine.write_delta_table()` | Parquet fallback active |
| Delta MERGE | `DatabricksDeltaEngine.merge_delta_table()` | Falls back to overwrite |
| Delta time travel | `DatabricksDeltaEngine.get_table_history()` | Falls back to stub |
| Databricks cloud Delta | **NOT YET IMPLEMENTED** | Cloud Delta via DBFS/Unity Catalog is new work |

---

## 4. Existing dbt Models

| Model | Path | Target | Status |
| :--- | :--- | :--- | :--- |
| `stg_transactions` | `dbt/models/staging/stg_transactions.sql` | DuckDB (`snowflake_warehouse.duckdb`) | ✅ Working |
| `int_fraud_summary` | `dbt/models/intermediate/int_fraud_summary.sql` | DuckDB | ✅ Working |
| `dim_customer` | `dbt/models/marts/dim_customer.sql` | DuckDB | ✅ Working |
| `fact_transactions` | `dbt/models/marts/fact_transactions.sql` | DuckDB | ✅ Working |
| Schema tests | `dbt/models/schema.yml` | `not_null`, `unique` | ✅ 3/3 passing |
| **dbt Databricks profile** | NOT PRESENT | — | ❌ Missing |

**dbt currently targets DuckDB (dev) and Snowflake (prod target in profiles.yml). Databricks target profile must be added.**

---

## 5. Existing PostgreSQL / SQLite Synchronization

| Component | Location | Behavior |
| :--- | :--- | :--- |
| Sync engine | `data_engineering/postgres_sync.py` | `PostgresGoldSync` |
| Primary target | PostgreSQL via `POSTGRES_URL` / `DATABASE_URL` env var | Falls back to SQLite in dev |
| SQLite fallback | `platform_analytics.db` | Active in current dev environment |
| Table created | `gold_multi_sector_summary` | 6-sector UPSERT rows |
| AI Copilot data | `ai/agent/metrics_tool.py` | Reads from `data/lake/gold/master_multi_sector_gold.json` |
| AI SQL tool | `ai/agent/sql_tool.py` | Reads from PostgreSQL → SQLite fallback |

---

## 6. Existing Docker Configuration

| File | Purpose |
| :--- | :--- |
| `docker-compose.yml` | Dev stack (backend, frontend, Redis) |
| `docker-compose.prod.yml` | Production configuration |
| `backend/Dockerfile` | Multi-stage backend build |
| `frontend/Dockerfile` | React multi-stage build |

**No Databricks-specific Docker components needed** (Databricks is a cloud service, not a container).

---

## 7. Existing Terraform

| File | Provisions |
| :--- | :--- |
| `infrastructure/terraform/main.tf` | GCP provider config |
| `infrastructure/terraform/gcp_resources.tf` | Cloud Run, GCS buckets (bronze/silver/gold), BigQuery dataset |
| `infrastructure/terraform/cost_controls.tf` | Budget alerts |
| `infrastructure/terraform/variables.tf` | GCP project, region variables |
| `infrastructure/terraform/outputs.tf` | Endpoint URLs |

**No Databricks Terraform resources exist.** A `databricks.tf` file will be needed for optional IaC (low priority — workspace already provisioned externally).

---

## 8. Existing GitHub Actions Workflows

| File | Jobs |
| :--- | :--- |
| `.github/workflows/ci.yml` | `test-python`, `build-frontend`, `docker-build`, `deploy-gcp-cloud-run` |
| `.github/workflows/ci-cd-security-gates.yml` | `pip-audit`, `npm-audit` |

**No Databricks job trigger step exists in CI.** A new job step will be needed for PAT-02 Databricks CI/CD integration (Phase 10 of this integration).

---

## 9. Existing BI / Superset Data Sources

| Component | Data Source | Notes |
| :--- | :--- | :--- |
| `bi/superset_init.py` | PostgreSQL (Gold sync target) | Superset SQL connection points to PostgreSQL |
| `bi/superset_sync.py` | Gold mart aggregations | Generates dashboard manifests |
| React BI dashboards | `backend/` REST API → SQLite/PostgreSQL | Real-time operational BI |
| `bi/superset_dashboards_manifest.json` | 7 dashboard configs | Offline manifest (Superset not running) |

**Databricks SQL can become an additional BI data source** alongside PostgreSQL — not a replacement.

---

## 10. Existing AI Copilot Data Access

| Tool | Data Source | Databricks opportunity |
| :--- | :--- | :--- |
| `MetricsTool` | `master_multi_sector_gold.json` (local file) | Could extend to query Databricks Gold |
| `ReadOnlySQLTool` | PostgreSQL → SQLite fallback | Could extend to query Databricks SQL Warehouse |
| `RAGTool` | FAISS vector index + HuggingFace embeddings | No change needed |
| `MLTool` | MLflow local model registry | No change needed |

---

## 11. Existing Tests

| Test File | Tests | What's Covered |
| :--- | :--- | :--- |
| `test_validation.py` | 3 | Gold data quality checks |
| `test_ogd_ingestion.py` | Multiple | Healthcare dataset ingestion |
| `test_credit_card_slice.py` | Multiple | Credit card vertical slice |
| `test_spark_pipeline.py` | Multiple | PySpark Medallion pipeline |
| `test_ml_engineering.py` | Multiple | XGBoost, LightGBM, RF models |
| `test_ai_copilot.py` | Multiple | RAG, intent router, SQL tool |
| `test_real_world_datasets.py` | Multiple | 6-sector dataset ingestion |
| `test_bi_superset.py` | Multiple | Superset manifest, Gold sync |
| `test_advanced_analytics.py` | Multiple | Clustering, anomaly, forecasting |
| `test_cloud_cicd.py` | Multiple | CI/CD config, Terraform structure |
| `test_deep_learning_nlp.py` | Multiple | PyTorch, HuggingFace |
| `test_data_engineering_stack.py` | 5 | Delta, Snowflake, dbt, CDC, governance |
| `test_resilience_chaos.py` | 4 | Redis/PG/Gemini offline + quarantine |
| **`test_databricks_integration.py`** | **0** | **MISSING — must be created** |

---

## 12. SDK / Package Status

| Package | Version | Status |
| :--- | :--- | :--- |
| `databricks-sdk` | **0.133.0** | ✅ **Already installed** |
| `requests` | 2.34.2 | ✅ Available (HTTP fallback) |
| `sqlalchemy` | 2.0.52 | ✅ Available |
| `databricks-sql-connector` | **Not installed** | ❌ Needed for SQL Warehouse ODBC/HTTP |

---

## 13. What Already Exists (Reusable)

| Item | Reuse Decision |
| :--- | :--- |
| `databricks-sdk` 0.133.0 | ✅ **Use as primary Databricks client library** |
| `DatabricksDeltaEngine` class | ✅ **Refactor** — rename to local-only, add new cloud client |
| `MultiSectorSparkPipeline` | ✅ **Reuse** — add cloud execution path alongside local |
| `PostgresGoldSync` | ✅ **Reuse** — add Databricks sync path alongside PostgreSQL |
| `master_multi_sector_gold.json` | ✅ **Canonical reconciliation reference** |
| `ReadOnlySQLTool` | ✅ **Extend** — add Databricks SQL Warehouse target |
| `MetricsTool` | ✅ **Extend** — add Databricks Gold data source |
| `dbt/profiles.yml` | ✅ **Extend** — add `databricks` output target |
| `.env.example` | ✅ **Extend** — add Databricks config vars |
| `run_tests.py` | ✅ **Extend** — add new Databricks test module |
| Existing 13 test files | ✅ **Must not regress** |

---

## 14. What Must Change (Modifications)

| File | Change |
| :--- | :--- |
| `.env.example` | Add `DATABRICKS_*` config vars |
| `dbt/profiles.yml` | Add `databricks` output target using `dbt-databricks` |
| `run_tests.py` | Import and register `TestDatabricksIntegration` |
| `README.md` | Add Databricks integration section |
| `.github/workflows/ci.yml` | Add optional Databricks job trigger step |

---

## 15. What Must NOT Change

| Item | Reason |
| :--- | :--- |
| `data_engineering/spark/spark_session.py` local mode | Local execution must continue working |
| All 13 existing test files | 55-test baseline must not regress |
| `data_engineering/postgres_sync.py` SQLite fallback | Dev environment must remain zero-dependency |
| `ai/agent/sql_tool.py` SQLite fallback | Copilot must remain functional offline |
| `data/lake/gold/master_multi_sector_gold.json` | Canonical Gold reference — must not be overwritten |
| `bi/superset_init.py` | Existing Superset configuration |
| `infrastructure/terraform/gcp_resources.tf` | Existing GCP Terraform |
| `frontend/` React app | No regression |
| All ML model files | No regression |

---

## 16. What Must Be Created (New Files)

```
data_engineering/databricks/
    __init__.py            — package init
    client.py              — workspace client, auth, connectivity
    jobs.py                — Jobs API (trigger, monitor, result)
    sql.py                 — SQL Statement Execution API (async poll)
    health.py              — connectivity / warehouse health check
    README.md              — engineering documentation

scripts/
    check_databricks.py    — health check script (no compute start)
    verify_databricks_runtime.py  — runtime verification (real SQL)

tests/
    test_databricks_integration.py  — mocked unit tests (10 scenarios)

docs/
    DATABRICKS_INTEGRATION_AUDIT.md   (this file)
    DATABRICKS_INTEGRATION.md         — full integration documentation
    SNOWFLAKE_INTEGRATION_PLAN.md     — Snowflake architecture plan
```

---

## 17. Estimated Completion

| Phase | Status | Effort |
| :--- | :--- | :--- |
| Audit | ✅ **DONE** | — |
| `.env.example` config | 🔲 Not started | 5 min |
| `data_engineering/databricks/` package | 🔲 Not started | 3–4 hrs |
| `scripts/check_databricks.py` | 🔲 Not started | 30 min |
| Runtime SQL verification (`SELECT 1`) | 🔲 Pending (warehouse up) | 15 min |
| Gold data reconciliation logic | 🔲 Not started | 1 hr |
| `tests/test_databricks_integration.py` | 🔲 Not started | 1 hr |
| `scripts/verify_databricks_runtime.py` | 🔲 Not started | 30 min |
| dbt profile extension | 🔲 Not started | 30 min |
| CI/CD Databricks job step | 🔲 Not started | 30 min |
| `docs/DATABRICKS_INTEGRATION.md` | 🔲 Not started | 1 hr |
| `docs/SNOWFLAKE_INTEGRATION_PLAN.md` | 🔲 Not started | 30 min |
| Interview Q&A extension | 🔲 Not started | 30 min |

**Estimated overall completion: ~8–10 hours of implementation work**

---

## 18. Risks

| Risk | Severity | Mitigation |
| :--- | :--- | :--- |
| OAuth PKCE flow requires browser redirect | HIGH | Use Databricks Personal Access Token (PAT) via `DATABRICKS_TOKEN` env var instead — standard for server-side automation |
| SQL Warehouse auto-suspended (2–5 min idle) | MEDIUM | health.py reports state clearly; `check_databricks.py` never auto-starts |
| `dbt-databricks` package version conflicts | MEDIUM | Install in separate step; existing dbt tests run on DuckDB and must not be disrupted |
| Databricks SDK auth on Windows | LOW | SDK supports `pat` token auth without browser; test on local first |
| Cloud cost overrun | LOW | Warehouse configured with auto-stop; `check_databricks.py` never starts compute |
| Unity Catalog may be enabled/restricted | MEDIUM | audit with `SELECT current_catalog()` before assuming `hive_metastore` |

---

## 19. Verification Status by Layer

| Layer | Local | Databricks Cloud |
| :--- | :---: | :---: |
| Bronze (Parquet) | ✅ UNIT VERIFIED | ❌ NOT YET |
| Silver (validated) | ✅ UNIT VERIFIED | ❌ NOT YET |
| Gold (aggregated) | ✅ UNIT VERIFIED | ❌ NOT YET |
| Gold (SQL table) | ✅ INTEGRATION VERIFIED (SQLite) | ❌ NOT YET |
| dbt models | ✅ INTEGRATION VERIFIED (DuckDB) | ❌ NOT YET |
| AI Copilot | ✅ UNIT VERIFIED | ❌ NOT YET |
| BI dashboards | ✅ UNIT VERIFIED (offline) | ❌ NOT YET |

---

## 20. Exact Next Steps (In Order)

1. **PHASE 2**: Update `.env.example` with `DATABRICKS_*` config vars (non-secret)
2. **PHASE 3**: Create `data_engineering/databricks/` package with `client.py`, `jobs.py`, `sql.py`, `health.py`
3. **PHASE 4**: Create `scripts/check_databricks.py` — verify configuration without starting compute
4. **PHASE 5**: With warehouse RUNNING, execute `SELECT 1` and `SELECT current_catalog(), current_schema(), current_user()` via `sql.py`
5. **PHASE 6**: Load existing Gold JSON into Databricks SQL (CREATE TABLE / INSERT or COPY) — no fake data
6. **PHASE 7**: Databricks Bronze → Silver → Gold execution path (notebook or job)
7. **PHASE 8**: Gold reconciliation — validate Databricks metrics == local canonical metrics
8. **PHASE 9**: Add `databricks` dbt profile target
9. **PHASE 10**: Add Databricks Jobs API job definition for the Medallion pipeline
10. **PHASE 11**: Create `docs/SNOWFLAKE_INTEGRATION_PLAN.md` (architecture only, no credentials)
11. **PHASE 12**: Create `tests/test_databricks_integration.py` (mocked unit tests)
12. **PHASE 13**: Document cost controls in `DATABRICKS_INTEGRATION.md`
13. **PHASE 14**: Update README, walkthrough, interview guide

---

## Summary

The platform already has **`databricks-sdk 0.133.0` installed**, an existing `DatabricksDeltaEngine` class (local-only), all 6 Gold sector data computed, and a SQL sync engine. The integration adds a **real cloud execution path** on top of the proven local pipeline — it does not replace any existing component.

**The warehouse is RUNNING. Ready to proceed to PHASE 2 on explicit approval.**
