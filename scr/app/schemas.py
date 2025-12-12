from pydantic import BaseModel
from typing import Optional


class PricesRequest(BaseModel):
    origin: str           # IATA код, например: LED
    destination: str      # IATA код
    depart_date: Optional[str] = None  # YYYY-MM-DD
    return_date: Optional[str] = None
    currency: str = "rub"             # rub, usd, eur


class CalendarRequest(BaseModel):
    origin: str
    destination: str
    month: str  # YYYY-MM
    currency: str = "rub"


class DirectRequest(BaseModel):
    origin: str
    destination: str
