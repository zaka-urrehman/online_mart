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
    size_id: int
    quantity: int

# Model for creating a new order
class OrderCreate(SQLModel):
    user_id: int
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
    user_id: int = Field(foreign_key="user.user_id")
    delivery_address: int = Field(foreign_key="useraddress.address_id")
    order_status: str = Field(default="pending")  # e.g., pending, shipped, delivered, etc.
    payment_status: str = Field(default="unpaid")  # e.g., paid, unpaid
    total_amount: float
    discount: float = 0.0
    net_amount: float  # total amount - discount
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships with User and OrderProducts
    user: Optional["User"] = Relationship(back_populates="orders")
    order_products: List["OrderProducts"] = Relationship(back_populates="order")



class OrderProducts(SQLModel, table=True):
    order_id: int = Field(foreign_key="order.order_id", primary_key=True)
    product_id: int = Field(foreign_key="product.product_id", primary_key=True)
    size_id: Optional[int] = Field(foreign_key="size.size_id", primary_key=True)
    quantity: int
    price_at_purchase: float  # Price of the product at the time of order

    # Relationships with Order, Product, and Size
    order: Optional["Order"] = Relationship(back_populates="order_products")
    product: Optional["Product"] = Relationship()
    size: Optional["Size"] = Relationship()


# ====================================================== CART MODELS =====================================================



class CartBase(SQLModel):
    """
    Base model for common fields in Cart-related models.
    """
    user_id: int
    product_id: int
    quantity: int = 1
    size_id: int  


class AddToCart(CartBase):
    """
    Model for validating data from the /add-to-cart API.
    Inherits fields from CartBase.
    """
    pass


class Cart(SQLModel, table=True):
    """
    Cart table to manage user carts.
    """
    cart_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    delivery_address: Optional[int] = Field(foreign_key="useraddress.address_id")
    nearest_branch: Optional[str] = None
    products_total: float = 0.0
    delivery_charges: float = 0.0
    discount: float = 0.0
    sub_total: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships with User and CartProduct
    user: Optional["User"] = Relationship(back_populates="carts")
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
    product_id: int = Field(foreign_key="product.product_id", primary_key=True)
    size_id: Optional[int] = Field(foreign_key="size.size_id", primary_key=True)  # Allowing NULL size_id
    quantity: int = 1

    # Relationships
    cart: Optional["Cart"] = Relationship(back_populates="cart_products")
    product: Optional["Product"] = Relationship()
    size: Optional["Size"] = Relationship()








# ================= COPY PASTING MODELS FROM OTHER SERVICES TO DEFINE CONNECTION BETWEEN TABLES =================
              # ======= also adding relationships with the Order and Order Product tables =======

# Define a regex pattern for validating emails
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
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
     # Relationship with Cart
    carts: List["Cart"] = Relationship(back_populates="user")
    # Relationship with Order
    orders: List["Order"] = Relationship(back_populates="user")

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
    order_products: List["OrderProducts"] = Relationship(back_populates="product")


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
    order_products: List["OrderProducts"] = Relationship(back_populates="size")


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



