-- Staging model for raw credit card transactions
SELECT 
    CAST(transaction_id AS VARCHAR) AS transaction_id,
    CAST(customer_id AS VARCHAR) AS customer_id,
    CAST(amount_usd AS DOUBLE) AS amount_usd,
    CAST(is_fraud AS INT) AS is_fraud,
    CAST(risk_score AS DOUBLE) AS risk_score,
    timestamp
FROM fact_transactions
