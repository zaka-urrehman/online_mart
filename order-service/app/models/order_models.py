import re

from sqlmodel import SQLModel, Field, Relationship
from typing import List
from datetime import datetime, timezone
from pydantic import field_validator, BaseModel
from  typing  import Optional


# ====================================================== ORDER MODELS =====================================================
# Model for a product item in the order
class OrderProductItem(BaseModel):
    product_id: int
    quantity: int
    product_price: int

# Model for creating a new order
class OrderCreate(SQLModel):
    user_id: int
    user_email: str
    cart_id: int
    products: List[OrderProductItem]
    delivery_address: Optional[int] = None
    nearest_branch: Optional[str] = None
    products_total: float = 0.0
    delivery_charges: float = 0.0
    discount: float = 0.0
    sub_total: float = 0.0

# Model for updating the order status
class OrderStatusUpdate(SQLModel):
    order_status: str

class Order(SQLModel, table=True):
    order_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int 
    delivery_address: int 
    order_status: str = Field(default="pending")  # e.g., pending, shipped, delivered, etc.
    payment_status: str = Field(default="unpaid")  # e.g., paid, unpaid
    total_amount: float
    discount: float = 0.0
    net_amount: float  # total amount - discount
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships with User and OrderProducts
    order_products: List["OrderProducts"] = Relationship(back_populates="order")



class OrderProducts(SQLModel, table=True):
    order_id: int = Field(foreign_key="order.order_id", primary_key=True)
    product_id: int = Field(primary_key=True)
    quantity: int
    price_at_purchase: float  # Price of the product at the time of order

    # Relationships with Order, Product, and Size
    order: Optional["Order"] = Relationship(back_populates="order_products")


# ====================================================== CART MODELS =====================================================



class CartBase(SQLModel):
    """
    Base model for common fields in Cart-related models.
    """
    user_id: int
    product_id: int
    quantity: int = 1


class AddToCart(CartBase):
    """
    Model for validating data from the /add-to-cart API.
    Inherits fields from CartBase.
    """
    product_price: float


class Cart(SQLModel, table=True):
    """
    Cart table to manage user carts.
    """
    cart_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    delivery_address: Optional[int]
    nearest_branch: Optional[str] = None
    products_total: float = 0.0
    delivery_charges: float = 0.0
    discount: float = 0.0
    sub_total: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships with User and CartProduct
    cart_products: List["CartProduct"] = Relationship(back_populates="cart")


class UpdateCart(SQLModel):
    """
    Model for updating cart information.
    """
    delivery_address: Optional[int] = Field(default=None, description="ID of the delivery address")
    nearest_branch: Optional[str] = Field(default=None, description="Nearest branch for delivery")
    discount: Optional[float] = Field(default=None, description="Discount applied to the cart")
    delivery_charges: Optional[float] = Field(default=None, description="Delivery charges for the cart")


class CartProduct(SQLModel, table=True):
    """
    Many-to-many relationship between Cart and Product.
    """
    cart_id: int = Field(foreign_key="cart.cart_id", primary_key=True)
    product_id: int = Field(primary_key=True)
    quantity: int = 1
    product_price: float

    # Relationships
    cart: Optional["Cart"] = Relationship(back_populates="cart_products")










