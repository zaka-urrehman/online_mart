from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Inventory(SQLModel, table=True):
    """
    Model for the Inventory table.
    """
    product_id: Optional[int] = Field(default=None, primary_key=True)
    cat_id: Optional[int] = Field(default=None)
    brand: Optional[str]
    expiry: Optional[datetime]
    price: Optional[float]
    quantity: Optional[int]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
