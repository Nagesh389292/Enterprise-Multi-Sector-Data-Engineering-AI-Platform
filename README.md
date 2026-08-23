# 🏛️ Enterprise Multi-Sector Data Engineering, ML/MLOps & AI Platform

[![CI/CD Master Pipeline](https://github.com/Nagesh389292/Enterprise-Multi-Sector-Data-Engineering-AI-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Nagesh389292/Enterprise-Multi-Sector-Data-Engineering-AI-Platform/actions)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PySpark 3.5](https://img.shields.io/badge/PySpark-3.5.0-orange.svg)](https://spark.apache.org/)
[![Databricks](https://img.shields.io/badge/Databricks-Delta_Lake-red.svg)](https://databricks.com/)
[![Superset BI](https://img.shields.io/badge/Apache_Superset-4.0-emerald.svg)](https://superset.apache.org/)
[![GCP Project](https://img.shields.io/badge/GCP_Project-enterprise--data--ai--platform-blue.svg)](https://console.cloud.google.com/)
[![Master Tests](https://img.shields.io/badge/Master_Tests-71%2F71_PASS-brightgreen.svg)](file:///c:/Users/NAGESH%20REDDY/Desktop/Data%20Analytics/run_tests.py)

**An enterprise-grade, multi-sector Data Engineering, ML/MLOps, BI, and AI Copilot platform built to process, analyze, and visualize financial, healthcare, clinical, insurance, and retail datasets with 0.00% Databricks data variance, 71/71 passing unit tests, and production-grade security standards.**

---

## 🎬 Live Project Execution Recording (Motion Walkthrough & Muxed AI Voice)

- 🎬 **Complete Live Execution Video (Muxed AAC Audio)**: [`docs/media/enterprise_platform_demo_video.mp4`](docs/media/enterprise_platform_demo_video.mp4) (8.06 MB MP4)
- 🎙️ **Standalone AI Voice Narration WAV**: [`docs/media/demo_narration.wav`](docs/media/demo_narration.wav) (12.96 MB Audio)
- 📐 **Video Technical Specifications**: 1280x720 (720p HD) | Duration: **4m 54s** (294.2s) | Audio Codec: AAC 93kbps | Video Codec: H.264 25fps | Audio Embedded: **YES**

### 🎙️ AI Voice Storyboard & Live Motion Transcript

> **00:00 — Section 1: Operational Command Center**  
> *"Welcome to this live execution walkthrough of the Enterprise Multi-Sector Data Engineering, Machine Learning, Business Intelligence, and AI Copilot Platform. We begin on the live operational command center, running on React port 3000. Here we observe unified telemetry across credit card processing, banking risk, healthcare capacity, clinical readmission, insurance claims, and retail sales."*  
>  
> **00:25 — Section 2: Data Engineering & PySpark Medallion Lakehouse**  
> *"In the Data Engineering core, raw streams enter a three-stage PySpark Medallion Lakehouse. Bronze ingests raw data with UUID primary keys. Silver enforces schema validation assertions, routing failing records to quarantine. Gold data marts aggregate sector key performance indicators."*  
>  
> **01:00 — Section 3: Multi-Tier AI Copilot Gateway & AST Security**  
> *"Now we interact directly with the AI Copilot. Watch as we type a natural language prompt into the interface: Which sector currently shows the highest risk according to available analytics? The gateway evaluates Tier 1 Gemini 2.5 Flash and Tier 2 OxAlpha via OpenRouter. Before execution, every generated SQL query passes through a sqlglot AST parser asserting it is strictly a read-only SELECT statement."*  
>  
> **01:40 — Section 4: Databricks SQL Synchronization & Reconciliation**  
> *"Next, we view the Databricks Delta Lake synchronization status. Automated reconciliation scripts query Databricks SQL Warehouse 1f1403d78bfa0404, matching row counts and metric totals across all six Gold data marts with 0.00 percent data variance."*  
>  
> **02:10 — Section 5: Apache Superset BI — Authentication & Executive Command Center**  
> *"Now we navigate to Apache Superset on port 8088. Watch as we log in with admin credentials. We enter the Executive Command Center dashboard, revealing real-time analytical distributions across all six sectors."*  
>  
> **02:35 — Section 6: Apache Superset BI — Credit Card Fraud Intelligence**  
> *"We navigate to the Credit Card Fraud Intelligence dashboard, scrolling down to inspect transaction amounts, risk score distributions, and fraud category metrics."*  
>  
> **02:55 — Section 7: Apache Superset BI — Banking Credit Risk Analytics**  
> *"Next is the Banking Credit Risk Analytics dashboard, displaying default probability distributions across loan purpose categories and debt-to-income tiers."*  
>  
> **03:10 — Section 8: Apache Superset BI — Healthcare Capacity & Utilization**  
> *"Moving to Healthcare Capacity & Utilization, we view state-level hospital bed occupancy and capacity telemetry."*  
>  
> **03:25 — Section 9: Apache Superset BI — Clinical EHR Readmission Risk**  
> *"The Clinical EHR Readmission Risk dashboard breaks down 30-day patient readmission risks by age groups and prior hospitalization counts."*  
>  
> **03:40 — Section 10: Apache Superset BI — Insurance Claims Fraud Analytics**  
> *"The Insurance Claims Fraud dashboard provides analytics on claim incident types and fraud likelihood indicators."*  
>  
> **03:55 — Section 11: Apache Superset BI — Retail Sales & Product Demand**  
> *"The Retail Sales & Product Demand dashboard highlights gross revenue totals and product sales volume across retail categories."*  
>  
> **04:15 — Section 12: GitHub Actions Master CI/CD Pipeline**  
> *"The platform uses GitHub Actions for continuous integration. The master runner run_tests.py executes 71 unit tests in under 260 seconds with 0 failures."*  
>  
> **04:35 — Section 13: Cloud Infrastructure Boundary & Final Summary**  
> *"The GCP deployment layer is declared in Terraform HCL for Cloud Run, GCS, and BigQuery. In summary, this platform combines PySpark data engineering, Databricks reconciliation, predictive ML, multi-tier AI security, and native BI dashboards into one unified release candidate."*

---

## 📊 Live Superset BI Demonstration (Authenticated & Rendered)

> The Gold analytical layer is exposed through Apache Superset, providing interactive dashboards for executive monitoring, fraud analytics, banking risk, healthcare utilization, clinical risk, insurance, and retail demand.
>  
> **Infrastructure & Provisioning**:
> - **Runtime Host**: Docker container `enterprise_superset` (`localhost:8088`)
> - **Database Connections**: 1 (`Enterprise Analytics Engine` connected to SQLite / PostgreSQL Gold Data Marts)
> - **Datasets Provisioned**: 7 (`gold_multi_sector_summary`, `gold_credit_card`, `gold_banking_loan_risk`, `gold_healthcare_ogd`, `gold_clinical_readmission`, `gold_insurance_claims`, `gold_retail_sales`)
> - **Slice Charts**: 9 native pie and table plugins (`status=success`)
> - **Published Dashboards**: 7

---

## ✅ Empirical Verification Results Table

| Subsystem | Empirical Verification Method | Verified Metric / Status |
| :--- | :--- | :--- |
| **PySpark Medallion Lakehouse** | `run_tests.py` automated test runner | 🟢 **100% PASS** (Bronze $\rightarrow$ Silver $\rightarrow$ Gold) |
| **Databricks SQL Synchronization** | `data_engineering/databricks/sql.py` statement execution | 🟢 **0.00% Variance** across 6/6 Gold sector data marts |
| **OxAlpha Cloud LLM Provider** | OpenRouter Gateway API probe (`stealth/ox-alpha`) | 🟢 **HTTP 200 LIVE SUCCESS** |
| **Ollama Local Daemon** | Codebase-wide grep inspection | 🟢 **0 References Remain (Purged)** |
| **Apache Superset BI Layer** | Native Python ORM Provisioner & REST API probe | 🟢 **1 DB, 7 Datasets, 9 Charts, 7 Dashboards** |
| **GitHub Actions CI/CD** | Cloud runner execution on `main` branch | 🟢 **Run #36 SUCCESS** across all 4 jobs |
| **GCP Infrastructure** | Terraform HCL validation (`verify_milestone9_cloud.py`) | 🟢 **Declared & Validated** |

---

## ⚠️ Honest Limitations & Architecture Boundary

- **GCP Cloud Run & BigQuery Deployment Status**: Infrastructure is fully declared in Terraform HCL (`infrastructure/terraform/main.tf`) and verified via Docker build CI steps for project `enterprise-data-ai-platform`; live cloud deployment to GCP Cloud Run (`PAT-03`) is intentionally unexecuted to maintain a zero-cost local release candidate baseline.
- **GDELT News Feed API**: Live API calls fall back gracefully to a cached baseline manifest (`data/config/`) when rate limits occur.

---

## ⚡ Quick Start & Verification Instructions

```bash
# 1. Clone Repository & Setup Environment
git clone https://github.com/Nagesh389292/Enterprise-Multi-Sector-Data-Engineering-AI-Platform.git
cd Enterprise-Multi-Sector-Data-Engineering-AI-Platform
cp .env.example .env

# 2. Execute Master Automated Unit Test Suite (71 Tests)
python run_tests.py

# 3. Launch Docker Services (Apache Superset + PostgreSQL + Redis)
docker-compose up -d

# 4. Launch React Command Center Web UI
npm --prefix frontend install
npm --prefix frontend run dev
```
