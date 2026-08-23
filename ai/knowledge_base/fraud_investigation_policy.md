# Enterprise Credit Card Fraud Investigation Policy & SOP

## 1. Overview & Objective
This Standard Operating Procedure (SOP) defines the operational guidelines for identifying, scoring, investigating, and resolving fraudulent credit card transactions across the enterprise data platform.

## 2. Risk Scoring & Classification Thresholds
All incoming real-time credit card transaction events are evaluated by the multi-model ML scoring engine (combining XGBoost, PyTorch Autoencoder, Isolation Forest, and SHAP explainability).

- **HIGH RISK (Score 70 - 100)**: Immediate automated block or step-up authentication required. Transaction sent to high-priority investigator queue.
- **MEDIUM RISK (Score 30 - 69)**: Flagged for secondary review; flagged if velocity exceeds 3 transactions within 5 minutes or z-score exceeds 2.0.
- **LOW RISK (Score 0 - 29)**: Standard processing; cleared automatically.

## 3. Specific Fraud Risk Indicators
1. **Unusual High Transaction Amount**: Any transaction amount exceeding $3,500.00 or exceeding 3.0 standard deviations from customer historical baseline (`amount_zscore > 3.0`).
2. **Velocity Spikes (`velocity_5m`)**: More than 3 transactions executed within a rolling 5-minute sliding window indicates potential automated card testing or botnet attack.
3. **Geographic Anomaly / Location Risk (`is_unusual_location = 1`)**: Transactions initiated from IP addresses or physical locations inconsistent with customer historical travel patterns or active session locations.
4. **Device Novelty (`is_new_device = 1`)**: First-time transaction attempt from an unverified hardware device fingerprint or unfamiliar browser agent.

## 4. Policy for Geographic Anomaly & High-Risk Flags
When a transaction exhibits an **Unusual Geographic Location** combined with an **unusual transaction amount** or **new device signature**:
- The platform automatically issues an advisory alert to the customer via SMS/Push notification.
- The transaction risk score is boosted to minimum 70 (HIGH RISK).
- Compliance investigators must inspect the SHAP feature attributions to confirm whether geographic distance or IP proxy/VPN usage was the primary attribution driver.

## 5. Escalation & Case Resolution
Investigators must log case resolutions into the PostgreSQL database under the `fraud_investigation_logs` table. Validated fraud cases update customer risk baselines and trigger automated chargeback processing.
