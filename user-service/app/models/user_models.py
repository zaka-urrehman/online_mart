from sqlmodel import SQLModel, Field, Relationship
from typing import List
from datetime import datetime, timezone
from pydantic import EmailStr

# Base class for common properties: email, phone
class UserBase(SQLModel):
    email: EmailStr
    phone: str

# 1. UserAuth Class
class UserAuth(UserBase):
    password: str

# 2. UserRegister Class
class UserRegister(UserAuth):
    first_name: str
    last_name: str

# 3. AddUserAddress Class
class AddUserAddress(UserBase):
    user_id: int
    lat: float | None = None
    lng: float | None = None
    gps_address: str | None = None
    city: str | None = None
    zip_code: str | None = None

# 4. User Class (Main table class with all fields)
class User(UserRegister, table=True):
    user_id: int | None = Field(default=None, primary_key=True)
    image: str | None = None
    role: str | None = None
    status: str | None = "active"  # default status is 'active'
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))


    # Relationship with UserAddress
    addresses: List["UserAddress"] = Relationship(back_populates="user")

# 5. UserAddress Class
class UserAddress(SQLModel, table=True):
    address_id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    lat: float | None = None
    lng: float | None = None
    gps_address: str | None = None
    city: str | None = None
    zip_code: str | None = None

    # Relationship with User
    user: User | None = Relationship(back_populates="addresses")
