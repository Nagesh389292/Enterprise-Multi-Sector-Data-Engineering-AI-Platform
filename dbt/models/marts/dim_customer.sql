-- Dimensional Customer Mart
SELECT
    c.customer_id,
    c.customer_name,
    c.account_type,
    c.risk_tier,
    f.total_transactions,
    f.total_amount_usd,
    f.fraud_transactions_count,
    f.avg_risk_score
FROM dim_customer c
LEFT JOIN {{ ref('int_fraud_summary') }} f
    ON c.customer_id = f.customer_id
