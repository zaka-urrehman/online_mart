import re
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import field_validator
# ==================== Base Models for Shared Fields ====================
class CategoryBase(SQLModel):
    cat_name: str
    description: Optional[str]

class ProductBase(SQLModel):
    product_name: str
    description: Optional[str]
    brand: Optional[str]
    expiry: Optional[datetime]
    price: float
    quantity: int

class SizeBase(SQLModel):
    size_name: str

# ==================== Category Models ====================
class AddCategory(CategoryBase):
    """
    Model for creating a new category (input).
    Inherits cat_name and description from CategoryBase.
    """
    pass

class Category(CategoryBase, table=True):
    """
    Full model for Category with all fields for response and database.
    """
    cat_id: Optional[int] = Field(default=None, primary_key=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    products: List["Product"] = Relationship(back_populates="category")


# ==================== Product Models ====================
class AddProduct(ProductBase):
    """
    Model for creating a new product (input).
    Inherits shared fields from ProductBase.
    """
    cat_id: Optional[int]  # Foreign key to the category

class Product(ProductBase, table=True):
    """
    Full model for Product with all fields for response and database.
    """
    product_id: Optional[int] = Field(default=None, primary_key=True)
    cat_id: Optional[int] = Field(default=None, foreign_key="category.cat_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: Optional["Category"] = Relationship(back_populates="products")
    sizes: List["ProductSize"] = Relationship(back_populates="product")


# ==================== Size Models ====================
class AddSize(SizeBase):
    """
    Model for creating a new size (input).
    Inherits size_name from SizeBase.
    """
    pass

class Size(SQLModel, table=True):
    """
    Full model for Size with all fields for response and database.
    """
    size_id: Optional[int] = Field(default=None, primary_key=True)
    size_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    products: List["ProductSize"] = Relationship(back_populates="size")


class SizeResponse(SQLModel):
    size_id: Optional[int]
    size_name: str
    created_at: datetime
    updated_at: datetime



# ==================== ProductSize Model ====================
class ProductSize(SQLModel, table=True):
    """
    Many-to-many relationship model between Product and Size.
    """
    product_id: Optional[int] = Field(default=None, foreign_key="product.product_id", primary_key=True)
    size_id: Optional[int] = Field(default=None, foreign_key="size.size_id", primary_key=True)

    # Relationships
    product: Optional["Product"] = Relationship(back_populates="sizes")
    size: Optional["Size"] = Relationship(back_populates="products")



# ====================== Copy Pasting Models from User Service to verify user from DB ======================
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

# 4. User Class (Main table class with all fields)
class User(UserRegister, table=True):
    user_id: int | None = Field(default=None, primary_key=True)
    image: str | None = None
    role: str | None = "user"
    status: str | None = "active"  # default status is 'active'
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))