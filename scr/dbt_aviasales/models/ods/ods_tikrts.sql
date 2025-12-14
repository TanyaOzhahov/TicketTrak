select
    id,
    request_id,
    origin,
    destination,
    airline,
    price,
    currency,
    departure_at::date as departure_date
from aviasales.tickets
where price is not null
