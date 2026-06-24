-- Staging model for transactions
-- By: Praneetha Meda

select
    transaction_id,
    timestamp,
    amount,
    is_fraud
from raw_transactions
