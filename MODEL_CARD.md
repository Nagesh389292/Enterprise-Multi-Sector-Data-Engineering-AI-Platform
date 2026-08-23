# 🎴 Master Model Cards & Scientific Validation Report

Authoritative Model Documentation for Enterprise Intelligence Platform.
Enforces strict distinction between **Champion Models** (production-serving) and **Challenger / Research Models**.

---

## 1. 💳 Credit Card Fraud Detection Models

### Champion Model: Random Forest / XGBoost Classifier
- **Task**: Real-Time Binary Fraud Classification ($0 = \text{Legitimate}, 1 = \text{Fraud}$)
- **Dataset**: ULB Credit Card Fraud Benchmark Dataset + Real-Time Stream Events
- **Class Imbalance**: $0.172\%$ Fraud ($492 / 284,807$ in full benchmark; $2,500$ sampled OOT evaluation set)
- **Data Splits**: 5-Fold Stratified Cross-Validation + 20% Temporal Out-of-Time (OOT) Holdout
- **Features (30)**: $V1 - V28$ PCA components, `Amount`, `Time`, plus online engineered `velocity_5m`, `amount_zscore`
- **Hyperparameters**:
  - `n_estimators`: 100
  - `max_depth`: 6
  - `learning_rate`: 0.05
  - `scale_pos_weight`: 5.0
- **Performance Metrics (OOT Realistic Topology)**:
  - **F1 Score**: $0.8066$ (Champion RF) / $0.7965$ (XGBoost)
  - **Precision**: $0.8245$
  - **Recall**: $0.7895$
  - **ROC-AUC**: $0.8939$
  - **PR-AUC**: $0.8120$
- **Inference Latency**: $0.85\text{ ms/batch}$
- **Operational Status**: 🟢 **CHAMPION MODEL (PRODUCTION SERVING)**

### Challenger Model 1: PyTorch Autoencoder (Unsupervised Anomaly)
- **Architecture**: Deep Autoencoder ($30 \rightarrow 14 \rightarrow 7 \rightarrow 14 \rightarrow 30$) with LeakyReLU & MSE Loss
- **Thresholding**: 95th Percentile Reconstruction Error ($MSE > 0.0412$)
- **Performance**: F1: $0.7420$ | Recall: $0.8520$ | Precision: $0.6570$
- **Operational Status**: 🟡 **CHALLENGER MODEL (ENSEMBLE RISK SCORE COMPONENT)**

### Challenger Model 2: PyTorch TransactionLSTM (Sequence Velocity)
- **Architecture**: 2-layer LSTM ($hidden\_dim=32$, $seq\_len=4$) trained on temporal sequence blocks
- **Training**: 2,497 sequence vectors evaluated with MSE Loss $0.5226$
- **Inference Latency**: $0.6947\text{ ms/sequence}$
- **Operational Status**: 🟡 **CHALLENGER MODEL (EXPERIMENTAL SEQUENCE CLASSIFIER)**
- **Limitations**: Requires at least 4 historical transactions per cardholder; defaults to XGBoost fallback for new users.

---

## 2. 🏦 Banking Credit Risk Model

### Champion Model: LightGBM Credit Risk Classifier
- **Task**: Default Risk Scoring ($0 = \text{Good Credit}, 1 = \text{High Default Risk}$)
- **Dataset**: German Credit Risk Benchmark Dataset ($1,800$ records)
- **Data Splits**: 80% Train / 20% Stratified Test
- **Features**: `account_balance`, `credit_duration`, `payment_status`, `credit_score`, `age`, `employment_years`
- **Performance Metrics**:
  - **F1 Score**: $0.7579$
  - **ROC-AUC**: $0.8145$
  - **Precision**: $0.7620$
  - **Recall**: $0.7538$
- **Unsupervised Segmentation**: K-Means ($k=3$) over 2 principal components explaining $51.3\%$ variance
- **Operational Status**: 🟢 **CHAMPION MODEL**

---

## 3. 🧬 Clinical EHR Readmission Model

### Champion Model: Random Forest Readmission Stratifier
- **Task**: 30-Day Hospital Readmission Risk ($0 = \text{No Readmit}, 1 = \text{Readmitted}$)
- **Dataset**: UCI Diabetes 130-US Hospitals EHR Dataset ($2,000$ sampled records)
- **Data Splits**: 5-Fold Cross-Validation
- **Threshold Calibration**: Precision-Recall AUC Optimal Threshold ($0.1499$)
- **Performance Metrics**:
  - **PR-AUC**: $0.4271$ (Baseline zero-rule: $0.1100$)
  - **F1 Score**: $0.2568$
  - **Recall at 80% Precision**: $0.3412$
- **Operational Status**: 🟢 **CHAMPION MODEL**
- **Limitations**: High class imbalance ($11\%$ readmit rate); threshold calibrated for high-precision notification queue.

---

## 4. 🛡️ Insurance Claims Fraud Model

### Champion Model: Isolation Forest Anomaly Queue + HF NLP
- **Task**: Claims Anomaly Scoring & Keyword Red Flag Detection
- **Dataset**: Kaggle Auto Insurance Claims Dataset ($1,500$ records)
- **Anomaly Scoring**: Isolation Forest (`contamination=0.08`) flagged $122$ high-risk claims
- **NLP Text Scanning**: Rule-based keyword matching over claim descriptions (`whiplash`, `staged`, `unwitnessed`, `delayed report`)
- **Operational Status**: 🟢 **CHAMPION MODEL**

---

## 5. 🏥 Healthcare & 🛒 Retail Demand Forecasting Models

### Champion Models: XGBoost Regressor Time-Series Engines
- **Healthcare Capacity Forecasting**: 7-Day hospital bed occupancy prediction ($MAE: 11.60$, $RMSE: 13.28$)
- **Retail Demand Forecasting**: Product demand prediction vs moving average baseline ($MAE: 12.65$, $354.4$ units forecast with $+15\%$ safety stock)
- **Operational Status**: 🟢 **CHAMPION MODELS**
