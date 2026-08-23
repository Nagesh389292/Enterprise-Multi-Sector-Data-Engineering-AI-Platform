# 🏛️ Enterprise-Grade Multi-Sector Data Engineering & AI Platform

[![CI/CD Master Pipeline](https://github.com/Nagesh389292/Enterprise-Multi-Sector-Data-Engineering-AI-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Nagesh389292/Enterprise-Multi-Sector-Data-Engineering-AI-Platform/actions)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PySpark 3.5](https://img.shields.io/badge/PySpark-3.5.0-orange.svg)](https://spark.apache.org/)
[![Databricks](https://img.shields.io/badge/Databricks-Delta_Lake-red.svg)](https://databricks.com/)
[![Superset BI](https://img.shields.io/badge/Apache_Superset-4.0-emerald.svg)](https://superset.apache.org/)
[![Master Tests](https://img.shields.io/badge/Master_Tests-71%2F71_PASS-brightgreen.svg)](file:///c:/Users/NAGESH%20REDDY/Desktop/Data%20Analytics/run_tests.py)

An enterprise-grade, multi-sector Data Engineering, ML/MLOps, BI, and AI Copilot platform built to process, analyze, and visualize financial, healthcare, clinical, insurance, and retail datasets with production-grade data quality, security, and verification standards.

---

## 🎯 Business Context & Verified Metrics

Modern enterprises require robust data infrastructure capable of processing heterogeneous datasets, detecting anomalies, providing interactive business intelligence, and exposing natural language AI interfaces securely.

- **71/71 Automated Master Unit Tests Passing**: 100% test coverage across 14 core modules (`run_tests.py`).
- **PySpark Medallion Lakehouse**: 3-stage Bronze $\rightarrow$ Silver $\rightarrow$ Gold pipeline with schema validation and quarantine routing.
- **Databricks SQL Synchronization**: 6 Gold sector data marts reconciled against Databricks SQL Warehouse (`1f1403d78bfa0404`) with **0.00% data variance**.
- **Multi-Tier AI Copilot + RAG**: Intent-based router (`AgenticRouter`) with Google Gemini 2.5 Flash, OxAlpha (`stealth/ox-alpha`) via OpenRouter Gateway (**HTTP 200 Live Verified**), FAISS vector store, and `sqlglot` AST Text-to-SQL security.
- **Native Apache Superset BI**: Programmatically provisioned via REST APIs with 1 DB, 7 SqlaTable datasets, 9 slice charts (`status=success`), and 7 published dashboards on Docker `localhost:8088`.
- **Master CI/CD**: 4-job GitHub Actions workflow (**Run #31 SUCCESS**) running Python tests, Vite React build, and multi-stage Docker builds.

---

## 🖼️ Visual Platform & Dashboard Demonstrations

### 1. Apache Superset BI Executive Command Center
![Apache Superset BI Dashboard](docs/images/superset_dashboard_demo.png)

### 2. React Command Center Web UI
![React Command Center Web UI](docs/images/react_command_center_ui.png)

### 3. System Architecture Topology
![System Architecture Diagram](docs/images/platform_architecture_diagram.png)

---

## 📐 Architecture Overview

```
                        LIVE EXTERNAL FEEDS & STREAMING
               (Alpha Vantage, OpenAQ, RBI Macro, Redis Streams)
                                │
                                ▼
                   PYSPARK MEDALLION LAKEHOUSE
            Bronze (Raw) ➔ Silver (Cleaned) ➔ Gold (Marts)
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
DATABRICKS DELTA LAKE   POSTGRESQL / SQLITE      APACHE SUPERSET BI
(0.00% Variance Sync)   (Gold Data Marts)     (7 Dashboards, 9 Charts)
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
                   ENTERPRISE AI COPILOT & RAG
             Agentic Router ➔ AST Read-Only SQL Security
        Gemini 2.5 Flash / OxAlpha (OpenRouter) ➔ Fallback
```

---

## 🚀 Quick Start Guide

```bash
# 1. Clone & Environment Setup
git clone https://github.com/Nagesh389292/Enterprise-Multi-Sector-Data-Engineering-AI-Platform.git
cd Enterprise-Multi-Sector-Data-Engineering-AI-Platform
cp .env.example .env

# 2. Execute Master Unit Test Suite
python run_tests.py

# 3. Launch Docker Services & React UI
docker-compose up -d
npm --prefix frontend install
npm --prefix frontend run dev
```

---

## ⚠️ Honest Limitations & Architecture Boundary

- **GCP Cloud Run & BigQuery**: Infrastructure is fully declared in Terraform HCL (`infrastructure/terraform/main.tf`) and verified via Docker build CI steps; live cloud deployment to GCP Cloud Run (`PAT-03`) is unexecuted to maintain a zero-cost local release candidate baseline.
- **GDELT News Feed**: API calls fall back gracefully to a cached baseline manifest (`data/config/`) when rate limits occur.
