# Apache Superset Native BI Runtime & Dashboard Evidence Report

**Verification Date**: 2026-08-23  
**Target Container**: `enterprise_superset` (`apache/superset:latest`)  
**Container URL**: `http://localhost:8088`  
**Database Backend**: PostgreSQL 16 (`enterprise_postgres:5432/enterprise_db`)  

---

## 1. Executive Summary

Empirical runtime verification confirms that Apache Superset has been fully provisioned with a native database connection, 7 SqlaTable datasets, 9 native visualization charts, and 7 published enterprise dashboards. Logging into `http://localhost:8088` displays live native Superset dashboards rendering multi-sector Gold data marts.

---

## 2. Verified Superset Resource Architecture & IDs

### A. Registered Database Connection
- **Database ID**: `1`
- **Database Name**: `Enterprise Analytics Engine`
- **Dialect / Driver**: `postgresql+psycopg2`
- **Target URI**: `postgresql+psycopg2://platform_user:******@postgres:5432/enterprise_db`
- **Connection Test Status**: 🟢 `SUCCESS`

### B. Registered Datasets (7 / 7)
| Dataset ID | Table Name | Business Sector / Purpose |
| :---: | :--- | :--- |
| **1** | `gold_multi_sector_summary` | Unified Cross-Sector Gold Data Mart |
| **2** | `gold_credit_card` | Credit Card Fraud & Transaction Risk |
| **3** | `gold_banking_loan_risk` | Banking Credit & Loan Default Risk |
| **4** | `gold_healthcare_ogd` | Healthcare Hospital Bed Occupancy & Capacity |
| **5** | `gold_clinical_readmission` | Clinical EHR 30-Day Readmission Risk |
| **6** | `gold_insurance_claims` | Auto Insurance Claims Fraud Analytics |
| **7** | `gold_retail_sales` | Retail Invoice Revenue & Demand Forecasting |

### C. Native Visualization Charts (9 / 9 — 0 Data Errors)
| Chart ID | Chart Slice Name | Viz Type | Table Datasource | Query Status | Data Rows |
| :---: | :--- | :---: | :--- | :---: | :---: |
| **1** | `Cross-Sector Metric Values` | Bar Chart | `gold_multi_sector_summary` | 🟢 `status=success` | 6 |
| **2** | `Total Records Processed by Sector` | Pie Chart | `gold_multi_sector_summary` | 🟢 `status=success` | 6 |
| **3** | `Credit Card Fraud Risk Breakdown` | Pie Chart | `gold_credit_card` | 🟢 `status=success` | 3 |
| **4** | `Transaction Amount vs Fraud Score` | Bar Chart | `gold_credit_card` | 🟢 `status=success` | 3 |
| **5** | `Banking Default Rate by Purpose` | Bar Chart | `gold_banking_loan_risk` | 🟢 `status=success` | 4 |
| **6** | `Healthcare Bed Occupancy by State` | Bar Chart | `gold_healthcare_ogd` | 🟢 `status=success` | 5 |
| **7** | `Clinical Readmission Risk by Age Group` | Bar Chart | `gold_clinical_readmission` | 🟢 `status=success` | 4 |
| **8** | `Insurance Fraud Probability by Incident Type` | Bar Chart | `gold_insurance_claims` | 🟢 `status=success` | 4 |
| **9** | `Retail Revenue by Product Category` | Pie Chart | `gold_retail_sales` | 🟢 `status=success` | 5 |

### D. Native Published Dashboards (7 / 7)
| Dashboard ID | Dashboard Title | Slug | Attached Chart IDs | Status |
| :---: | :--- | :--- | :---: | :---: |
| **1** | `Executive Command Center` | `executive-command-center` | `1`, `2` | 🟢 Published |
| **2** | `Credit Card Fraud Intelligence` | `fraud-intelligence` | `3`, `4` | 🟢 Published |
| **3** | `Banking Credit Risk Analytics` | `banking-credit-risk` | `5` | 🟢 Published |
| **4** | `Healthcare Capacity & Utilization` | `healthcare-utilization` | `6` | 🟢 Published |
| **5** | `Clinical EHR Readmission Risk` | `clinical-readmission` | `7` | 🟢 Published |
| **6** | `Insurance Claims Fraud Analytics` | `insurance-claims-fraud` | `8` | 🟢 Published |
| **7** | `Retail Sales & Product Demand` | `retail-demand-revenue` | `9` | 🟢 Published |

---

## 3. REST API & Automated Test Verification Output

### REST API Query Response (`http://localhost:8088/api/v1/`)
```json
{
  "status": "SUCCESS",
  "superset_url": "http://localhost:8088",
  "authenticated": true,
  "container_provisioned": true,
  "databases_count": 1,
  "datasets_count": 7,
  "charts_count": 9,
  "dashboards_provisioned_count": 7
}
```

### Automated Unit Test Execution (`python -m unittest tests.test_bi_superset`)
```text
test_dashboard_configs_count (tests.test_bi_superset.TestBISuperset) ... ok
test_superset_provisioning_export (tests.test_bi_superset.TestBISuperset) ... ok

----------------------------------------------------------------------
Ran 2 tests in 8.533s

OK
```
