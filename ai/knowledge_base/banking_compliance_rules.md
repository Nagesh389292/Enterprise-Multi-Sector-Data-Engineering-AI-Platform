# Banking Compliance & Financial Regulations Guide

## 1. Regulatory Overview
Enterprise financial systems must comply with Anti-Money Laundering (AML), Bank Secrecy Act (BSA), and Reserve Bank of India / Financial Intelligence Unit guidelines.

## 2. Key AML & Transaction Monitoring Rules
- **Large Value Threshold (CTR)**: All cash or card transactions exceeding $10,000 (or equivalent INR) must trigger an automated Currency Transaction Report (CTR) record.
- **Structuring & Smurfing**: Multiple transactions occurring within 24 hours under the $10,000 threshold that aggregate to over $10,000 are flagged as suspicious structuring.
- **Dormant Account Activation**: Sudden high-velocity activity on accounts dormant for > 180 days triggers an automated fraud freeze (`is_new_device = 1`, `velocity_5m > 2`).

## 3. Customer Due Diligence (CDD) & Risk Tiering
Customers are classified into three risk tiers based on transaction history and KYC verification:
- **Tier 1 (Low Risk)**: Verified KYC, stable monthly transaction volumes.
- **Tier 2 (Moderate Risk)**: Cross-border transactions, high monthly velocity.
- **Tier 3 (High Risk / Politically Exposed Persons)**: Continuous automated monitoring, mandatory manual approval for transfers > $5,000.
