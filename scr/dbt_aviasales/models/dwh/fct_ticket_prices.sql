select
    origin,
    destination,
    departure_date,
    airline,
    count(*)            as tickets_count,
    min(price)          as min_price,
    avg(price)          as avg_price,
    max(price)          as max_price
from {{ ref('ods_tickets') }}
group by
    origin,
    destination,
    departure_date,
    airline
