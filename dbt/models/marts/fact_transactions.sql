-- Fact Transactions Mart
SELECT
    transaction_id,
    customer_id,
    amount_usd,
    is_fraud,
    risk_score,
    timestamp
FROM {{ ref('stg_transactions') }}
