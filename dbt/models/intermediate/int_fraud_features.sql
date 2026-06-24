-- Intermediate model with enriched features
-- By: Praneetha Meda

select
    transaction_id,
    timestamp,
    amount,
    is_fraud,
    case when amount > 1000 then 1 else 0 end as high_amount_flag
from {{ ref('stg_transactions') }}
