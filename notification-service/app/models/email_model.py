import re 
from sqlmodel import SQLModel, Field, Column , DateTime 
from pydantic import field_validator
from enum import Enum
from datetime import datetime

class NotificationTypeEnum(str, Enum):
    REGISTER_ALERT = "register alert"
    LOGIN_ALERT = "login alert"
    PRODUCT_ALERT = "product alert"
    INVENTORY_ALERT = "inventory alert"

# Define a regex pattern for validating emails
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


# Base class for common properties: email, phone
class NotificationBase(SQLModel):
    email: str
    title: str
    message: str 

     # Custom validator to ensure the email matches the regex pattern
    @field_validator('email')
    def validate_email(cls, value):
        if not EMAIL_REGEX.match(value):
            raise ValueError('Invalid email address')
        return value
    

class Notification(NotificationBase, table=True):
    id: int = Field(default=None, primary_key=True)
    notification_type: NotificationTypeEnum
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: datetime = Field(default=None, sa_column=Column(DateTime, nullable=True))
