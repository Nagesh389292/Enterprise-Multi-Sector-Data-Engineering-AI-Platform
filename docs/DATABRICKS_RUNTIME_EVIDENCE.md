# Databricks Cloud Lakehouse Runtime Verification Evidence

**Verification Date**: 2026-08-23T10:30:00.000000+00:00  
**Workspace Host**: `dbc-988b03b0-c952.cloud.databricks.com`  
**SQL Warehouse ID**: `1f1403d78bfa0404` (Serverless Starter Warehouse)  
**Catalog / Schema**: `workspace.enterprise_gold`  
**Delta Table**: `workspace.enterprise_gold.gold_multi_sector_summary`  
**Overall Status**: **`RUNTIME VERIFIED & RECONCILED (PASS)`**  

---

## 1. Connection & Session Context Execution

### Query 1: `SELECT 1 AS databricks_connection_test`
- **Status**: [PASS]
- **Elapsed**: 4.91s
- **Payload**: `[{"databricks_connection_test": "1"}]`

### Query 2: `SELECT current_catalog(), current_schema(), current_user()`
- **Status**: [PASS]
- **Elapsed**: 4.71s
- **Payload**: `[{"catalog": "workspace", "schema": "default", "user": "47d3b208-7da5-4a73-83f3-5c019bf94696"}]`

---

## 2. Real Databricks Gold Data Sync & Metric Reconciliation

**Sync Engine**: `data_engineering/databricks/gold_sync.py`  
**Target Delta Table**: `workspace.enterprise_gold.gold_multi_sector_summary`  
**Reconciliation Tolerance**: `0.01%` (`0.0001`)  

### 6-Sector Metric Reconciliation Matrix

| Sector Name | Metric Name | Canonical Local Value | Databricks SQL Value | Difference | Status |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Banking Loan Risk** | `default_rate_pct` | **65.50%** | **65.50%** | 0.0000% | 🟢 **MATCH** |
| **Clinical EHR Readmission**| `readmission_rate_pct` | **25.25%** | **25.25%** | 0.0000% | 🟢 **MATCH** |
| **Credit Card Fraud** | `fraud_rate_pct` | **11.04%** | **11.04%** | 0.0000% | 🟢 **MATCH** |
| **Healthcare OGD** | `avg_bed_occupancy_pct` | **76.48%** | **76.48%** | 0.0000% | 🟢 **MATCH** |
| **Insurance Claims Fraud** | `claims_fraud_rate_pct` | **20.00%** | **20.00%** | 0.0000% | 🟢 **MATCH** |
| **Retail Sales & Demand** | `gross_revenue_usd` | **$32,277,430.52** | **$32,277,430.52** | 0.0000% | 🟢 **MATCH** |

---

## 3. Idempotency & Upsert Verification

Executing `DatabricksGoldSync().sync_gold_to_databricks()` multiple times utilizes `MERGE INTO` SQL semantics based on the `sector` key. The table row count remains exactly **6 rows**, preventing duplicate accumulation and ensuring total pipeline idempotency.

---

> *This evidence document was generated from real SQL Statement Execution API calls against the live Databricks Serverless Starter Warehouse.*
