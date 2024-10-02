import re

from sqlmodel import SQLModel, Field, Relationship
from typing import List
from datetime import datetime, timezone
from pydantic import field_validator


# Define a regex pattern for validating emails
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')



# Base class for common properties: email, phone
class UserBase(SQLModel):
    email: str
    phone: str

     # Custom validator to ensure the email matches the regex pattern
    @field_validator('email')
    def validate_email(cls, value):
        if not EMAIL_REGEX.match(value):
            raise ValueError('Invalid email address')
        return value

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
    role: str | None = "user"
    status: str | None = "active"  # default status is 'active'
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))

    # TODO: include otp later

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
