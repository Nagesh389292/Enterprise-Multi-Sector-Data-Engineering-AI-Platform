-- Intermediate model calculating customer-level fraud aggregations
SELECT
    customer_id,
    COUNT(transaction_id) AS total_transactions,
    SUM(amount_usd) AS total_amount_usd,
    SUM(is_fraud) AS fraud_transactions_count,
    AVG(risk_score) AS avg_risk_score
FROM {{ ref('stg_transactions') }}
GROUP BY customer_id
