-- Final fact table for analytics
-- By: Praneetha Meda

select
    transaction_id,
    timestamp,
    amount,
    is_fraud,
    high_amount_flag,
    current_timestamp as processed_at
from {{ ref('int_fraud_features') }}
