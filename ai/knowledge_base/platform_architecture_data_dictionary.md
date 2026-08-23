# Enterprise Data & AI Platform Architecture & Data Dictionary

## 1. System Architecture Overview
The platform implements an end-to-end real-time and batch enterprise data pipeline:

```
Real-Time Ingestion (Redis Stream 'credit_card_events')
    ↓
Streaming Validation & Sliding Window Feature Store
    ↓
Multi-Model Inference (XGBoost + PyTorch Autoencoder + SHAP)
    ↓
PostgreSQL & SSE Event Stream
    ↓
React Real-Time Command Center

Batch Pipeline:
Raw Files -> PySpark Medallion (Bronze Parquet -> Silver Clean -> Gold Marts) -> PostgreSQL Sync
```

## 2. Key Data Tables & Schema Dictionary

### PostgreSQL / Gold Table: `credit_card_transactions`
- `event_id` (VARCHAR PK): Unique transaction identifier (e.g., `TXN-45728`).
- `customer_id` (VARCHAR): Customer identifier (e.g., `C1029`).
- `amount` (FLOAT): Transaction amount in USD.
- `merchant` (VARCHAR): Merchant category / name (e.g., `Electronics`, `Travel`).
- `location` (VARCHAR): Transaction geographic city/country location.
- `device_id` (VARCHAR): Device hardware fingerprint ID.
- `fraud_probability` (FLOAT): Model output probability (0.0 to 1.0).
- `risk_score` (INT): Scaled risk score (0 to 100).
- `risk_level` (VARCHAR): Risk classification (`LOW`, `MEDIUM`, `HIGH`).
- `is_fraud_predicted` (INT): Binary prediction flag (1 = fraud, 0 = normal).
- `created_at` (TIMESTAMP): Event ingestion timestamp.

### Gold Mart: `credit_card_gold_mart`
- `total_transactions` (INT): Total count of processed transactions.
- `total_fraud_count` (INT): Count of flagged high-risk transactions.
- `fraud_rate_pct` (FLOAT): Percentage of transactions flagged as fraud (`total_fraud_count / total_transactions * 100`).
- `total_volume_usd` (FLOAT): Sum of all transaction amounts.
- `high_risk_merchants` (ARRAY): Top merchants with elevated fraud concentration.

## 3. MLOps Model Registry & Champion Management
- Champion model is dynamically evaluated and promoted based on validation metrics stored in SQLite `mlflow.db`.
- Supported Model Families: `Logistic Regression`, `Random Forest`, `XGBoost`, `LightGBM`, `Isolation Forest`, `PyTorch Autoencoder`.
- SHAP (SHapley Additive exPlanations) values provide human-readable attribution reasons for high-risk flags.
