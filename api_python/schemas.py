from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PosPriceSchema(BaseModel):
    store_nbr: int
    item_nbr: str
    upc_code: str
    upc_description: Optional[str] = None
    previous_base_price: float
    new_base_price: float
    previous_customer_price: float
    new_customer_price: float
    modification_date: datetime

class PriceFilter(BaseModel):
    store_nbr: Optional[int] = None
    item_nbr: Optional[str] = None
    upc_code: Optional[str] = None

class DpfilePosSchema(BaseModel):
    store_nbr: int
    pos_nbr: str      
    ip_nbr: str
    modification_date: datetime
    size_bytes: int

class PmtDpcSchema(BaseModel):
    name_pmt: str
    store_nbr: int
    modification_date: datetime
    size_bytes: int

class PromoFilter(BaseModel):
    store_nbr: int 
    pos_nbr: Optional[str] = None

