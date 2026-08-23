# Insurance Claims Processing & Risk Analytics Guide

## 1. Overview
The Insurance vertical analytics pipeline evaluates claims for auto, health, and property insurance policies to detect fraudulent claims, duplicate billing, and inflated estimates.

## 2. Key Insurance Metrics
- **Loss Ratio**: Total claims paid out divided by total earned premiums. Benchmark target: < 65%.
- **Claims Settlement Ratio (CSR)**: Percentage of filed claims approved and settled within 30 days.
- **Fraud Claim Anomaly Score**: Combined Machine Learning risk score assessing claim amount z-score, provider historical fraud rate, and policy age.
- **Duplicate Claim Detection**: Automated fuzzy matching on incident date, location, claimant ID, and loss description.
