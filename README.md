# Enterprise Multi-Sector Data & AI Intelligence Platform

[![Release Candidate](https://img.shields.io/badge/Status-Release%20Candidate%20(RC)-green.svg)](#)
[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue.svg)](.github/workflows/ci.yml)
[![Master Unit Tests](https://img.shields.io/badge/Tests-65%2F65%20Passing-brightgreen.svg)](run_tests.py)
[![Databricks](https://img.shields.io/badge/Databricks-Cloud%20Data%20Engineering-red.svg)](data_engineering/databricks/)
[![npm audit](https://img.shields.io/badge/npm%20audit-0%20vulnerabilities-brightgreen.svg)](npm_audit_report.json)
[![PAT-04](https://img.shields.io/badge/PAT--04-Security%20Audit%20Conditional%20Pass-yellow.svg)](PAT_04_SECURITY_AUDIT_REPORT.md)
[![Snowflake](https://img.shields.io/badge/Snowflake-Star%20Schema%20DW-blue.svg)](data_engineering/snowflake_dw.py)
[![dbt](https://img.shields.io/badge/dbt-Analytics%20Engineering-orange.svg)](dbt/)
[![PySpark](https://img.shields.io/badge/PySpark-4.2.0-orange.svg)](data_engineering/spark/)
[![MLOps](https://img.shields.io/badge/ML-XGBoost%20%7C%20PyTorch-green.svg)](ml/)
[![Infrastructure](https://img.shields.io/badge/GCP-Ready%20for%20Deployment-blue.svg)](infrastructure/terraform/)

A feature-complete, technically hardened Enterprise Data Engineering, Analytics Engineering, Databricks Delta Lakehouse, Snowflake Data Warehouse, dbt Modeling, Data Governance, Machine Learning, BI, and AI Copilot platform processing analytical workflows across **Credit Card Fraud**, **Banking Credit Risk**, **Healthcare Utilization**, **Clinical EHR Readmission**, **Insurance Claims Fraud**, and **Retail Demand Forecasting**.

---

## ⏱️ 5-Minute High-Level Architecture Flow

```text
                                SOURCES
                                   │
                  ┌────────────────┼────────────────┐
                  ▼                ▼                ▼
               APIs/Files      Redis Streams     Documents
                  │                │                │
                  └────────────────┼────────────────┘
                                   ▼
                              INGESTION
                                   │
                           Airflow / Jobs
                                   │
                                   ▼
                              PySpark
                                   │
                         ┌─────────┴─────────┐
                         ▼                   ▼
                      Bronze              Delta
                         │               Lakehouse
                         ▼                   │
                      Silver ◄───────────────┘
                         │
                         ▼
                        Gold
                         │
               ┌─────────┼──────────┐
               ▼         ▼          ▼
           Databricks Snowflake PostgreSQL
           Lakehouse   Warehouse  OLTP/API
               │         │
               └────┬────┘
                    ▼
                   dbt
                    │
                    ▼
              Analytical Marts
                    │
             ┌──────┴──────┐
             ▼             ▼
           BI            ML/AI
        Superset         MLflow
        React            XGBoost
                         LSTM
                         NLP
                           │
                           ▼
                      AI Copilot
                   SQL + RAG + ML
                           │
                           ▼
                         GCP
                   Docker / Terraform
                           │
                     GitHub Actions
```

---

## 🏛️ Comprehensive Architecture

```text
                                REAL-TIME & BATCH DATA SOURCES
    (Credit Card Streams, Banking Risk, Healthcare OGD, Clinical EHR, Insurance Claims, Retail Sales)
                                                │
                                                ▼
                             PYSPARK 4.2.0 MEDALLION LAKEHOUSE
                          Bronze Parquet ──► Silver ──► Gold Marts
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 ▼                              ▼                              ▼
      MACHINE LEARNING & MLOPS         PREDICTIVE ANALYTICS ENGINE      BI & SUPERSET LAYER
   (XGBoost, LightGBM, RF, Autoencoder) (Time-Series, Clustering, PR-AUC) (7 Interactive Dashboards)
                 │                              │                              │
                 └──────────────────────────────┼──────────────────────────────┘
                                                ▼
                                     ENTERPRISE AI COPILOT
                          (RAG Vector DB, Intent Router, Tool Agent)
                                                │
                                                ▼
                         REACT COMMAND CENTER & GCP CLOUD RUN DEPLOYMENT
                             (GitHub Actions CI/CD + Terraform IaC)
```

---

## 📊 Sector Analytics Breakdown & Saturation Performance

| Domain / Sector | Data Engine | Machine Learning / Analytics Model | Champion Metric |
| :--- | :--- | :--- | :---: |
| **💳 Credit Card Fraud** | Redis Stream + PySpark | Champion RF / XGBoost + PyTorch Autoencoder | **F1: 0.8066 \| AUC: 0.8939** |
| **🏦 Banking Risk** | PySpark Medallion | LightGBM + K-Means Clustering ($k=3$) + PCA | **F1: 0.7579 \| 51.3% Var** |
| **🏥 Healthcare Capacity** | MoHFW OGD Pipeline | XGBoost Regressor 7-Day Time-Series | **MAE: 11.60 \| RMSE: 13.28** |
| **🧬 Clinical EHR** | UCI Diabetes 130-US | Random Forest + PR-AUC Threshold Calibration | **PR-AUC: 0.4271 \| F1: 0.2568** |
| **🛡️ Insurance Claims** | Kaggle Auto Insurance | Isolation Forest Anomaly Queue + HF NLP | **122 High-Risk Claims** |
| **🛒 Retail Demand** | UCI Online Retail | XGBoost Regressor vs Moving Average | **MAE: 12.65 \| 354.4 Units** |

### ⚡ Empirical Performance & Concurrency Saturation Benchmarks
- **Peak Observed Throughput**: $28.21\text{ events/sec}$ (under 25-worker parallel stress test)
- **Multi-Worker Concurrency Profile**:
  - **10 Workers**: $27.53\text{ eps} \mid p50: 68.69\text{ ms} \mid p95: 140.43\text{ ms} \mid 0.0\%\text{ errors}$
  - **25 Workers**: $28.21\text{ eps} \mid p50: 191.17\text{ ms} \mid p95: 335.22\text{ ms} \mid 0.0\%\text{ errors}$
  - **50 Workers**: $27.21\text{ eps} \mid p50: 400.33\text{ ms} \mid p95: 599.40\text{ ms} \mid 0.0\%\text{ errors}$
  - **100 Workers**: $26.11\text{ eps} \mid p50: 778.72\text{ ms} \mid p95: 1237.64\text{ ms} \mid 0.0\%\text{ errors}$
- **PyTorch LSTM Inference Latency**: $0.6947\text{ ms/sequence}$
- **PySpark Medallion Throughput**: $5,102.04\text{ rows/sec}$
- **React Frontend Production Bundle**: $179.94\text{ kB}$ JS (Gzip: $53.5\text{ kB}$), $2.29\text{ kB}$ CSS (Gzip: $1.0\text{ kB}$)

---

## 🛠️ Technology Stack

- **Big Data & Data Lakehouse**: PySpark 4.2.0, Parquet (Bronze / Silver / Gold), PostgreSQL, SQLite Fallback.
- **Real-Time Streaming**: Redis Stream Producer/Consumer, Online Validation Engine.
- **Machine Learning & MLOps**: XGBoost, LightGBM, Random Forest, PyTorch Autoencoder & LSTM, SHAP, MLflow Registry.
- **Predictive Analytics**: K-Means Clustering, PCA, Isolation Forest Anomaly Queue, PR-AUC Threshold Calibration, XGBoost Time-Series Forecasting.
- **AI Copilot & RAG**: FAISS Vector Index, Hugging Face Dense Embeddings, Multi-Tier Intent Router, Read-Only SQL Tool.
- **Business Intelligence**: React BI Dashboards, Apache Superset Automated Configuration Initializer.
- **DevOps & Infrastructure**: Docker Multi-Stage Builds, Docker Compose, Terraform GCP IaC (Cloud Run, Cloud Storage, BigQuery), GitHub Actions CI/CD.

---

## 🚀 Quickstart & Verification

### 1. Run Master Unit Test Runner (50 / 50 Tests Passing)
```bash
python run_tests.py
```

### 2. Run Automated Resilience & Chaos Failure Test Suite
```bash
python -m unittest tests/test_resilience_chaos.py
```

### 3. Run Multi-Worker Concurrency Saturation Benchmark
```bash
python benchmarks/load_test.py
```

### 4. Build & Serve React Command Center Frontend
```bash
cd frontend
npm ci
npm run build
```

---

## 🔒 Security & Deployment Architecture

- **Credential Exposure Audit**: Scanned 184 files with `security_audit.py` (**0 leaks detected**). 15-domain controls documented in [`SECURITY_AUDIT.md`](SECURITY_AUDIT.md).
- **PAT-04 Dependency Audit**: `pip-audit` (112 packages, 0 High/Critical CVEs) + `npm audit` (**0 vulnerabilities** post Vite v8 upgrade). Full report: [`PAT_04_SECURITY_AUDIT_REPORT.md`](PAT_04_SECURITY_AUDIT_REPORT.md).
- **Terraform IaC**: Declarative GCP Cloud Run (`enterprise-platform-api`), GCS Buckets (`enterprise-lake-bronze/silver/gold`), and BigQuery Gold Dataset (`enterprise_platform_gold`) provisioning in `infrastructure/terraform/`.
- **Cost Controls**: Configured budget alerts ($5 monthly threshold) and Cloud Run scale-to-zero caps to control cloud spend.
- **CI/CD Pipeline**: GitHub Actions `.github/workflows/ci.yml` defining automated unit testing, frontend builds, Docker container builds, and GCP deployment.

---

## 📋 Portfolio & Interview Resources

- **[PORTFOLIO_SUMMARY.md](PORTFOLIO_SUMMARY.md)** — Single-page project overview with all technology coverage, metrics, and talking points.
- **[docs/interview_defense_guide.md](docs/interview_defense_guide.md)** — 18 senior technical interview Q&A pairs covering every architectural decision.
- **[PAT_ROADMAP.md](PAT_ROADMAP.md)** — Formal production acceptance testing gates and release criteria.
- **[SECURITY_AUDIT.md](SECURITY_AUDIT.md)** — OWASP-aligned 15-domain security control matrix.
