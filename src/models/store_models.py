"""
Store Models
Pydantic models for store module (products, cart, customer orders)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator


class ProductBase(BaseModel):
    """Product model"""
    product_id: Optional[int] = Field(None, description="Product ID")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: str = Field(..., description="Product category")
    subcategory: str = Field(..., description="Product subcategory")
    price: Decimal = Field(..., ge=0, description="Product price")
    image_url: Optional[str] = Field(None, description="Product image URL")
    stock_quantity: int = Field(0, ge=0, description="Available stock")
    is_active: bool = Field(True, description="Is product active")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    """Model for creating a new product"""
    name: str
    description: Optional[str] = None
    category: str
    subcategory: str
    price: Decimal
    image_url: Optional[str] = None
    stock_quantity: int = 0
    is_active: bool = True


class ProductUpdate(BaseModel):
    """Model for updating a product"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    price: Optional[Decimal] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None


class CartItem(BaseModel):
    """Shopping cart item"""
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int = Field(..., gt=0)
    subtotal: Decimal

    @validator('subtotal', always=True)
    def calculate_subtotal(cls, v, values):
        """Calculate subtotal automatically"""
        if 'product_price' in values and 'quantity' in values:
            return values['product_price'] * values['quantity']
        return v


class Cart(BaseModel):
    """Shopping cart"""
    items: List[CartItem] = []
    subtotal: Decimal = Decimal('0.00')
    tax_rate: Decimal = Field(Decimal('0.08'), description="Tax rate (8%)")
    tax_amount: Decimal = Decimal('0.00')
    shipping_cost: Decimal = Decimal('0.00')
    total: Decimal = Decimal('0.00')

    def calculate_totals(self):
        """Calculate cart totals"""
        self.subtotal = sum(item.subtotal for item in self.items)
        self.tax_amount = self.subtotal * self.tax_rate

        # Free shipping over $100, otherwise $10
        if self.subtotal >= 100:
            self.shipping_cost = Decimal('0.00')
        else:
            self.shipping_cost = Decimal('10.00')

        self.total = self.subtotal + self.tax_amount + self.shipping_cost


class CustomerInfo(BaseModel):
    """Customer information for checkout"""
    customer_name: str = Field(..., min_length=2)
    customer_email: EmailStr
    customer_phone: Optional[str] = None
    shipping_address: str = Field(..., min_length=5)
    shipping_city: str = Field(..., min_length=2)
    shipping_state: Optional[str] = None
    shipping_zip: str = Field(..., min_length=3)
    shipping_country: str = Field(default="USA")
    notes: Optional[str] = None


class OrderItemBase(BaseModel):
    """Order item model"""
    order_item_id: Optional[int] = None
    customer_order_id: Optional[int] = None
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int = Field(..., gt=0)
    subtotal: Decimal
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerOrderBase(BaseModel):
    """Customer order model"""
    customer_order_id: Optional[int] = None
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: str
    shipping_city: str
    shipping_state: Optional[str] = None
    shipping_zip: str
    shipping_country: str
    subtotal_amount: Decimal = Field(..., ge=0)
    tax_amount: Decimal = Field(..., ge=0)
    shipping_cost: Decimal = Field(..., ge=0)
    total_amount: Decimal = Field(..., ge=0)
    status: str = Field(default="pending")
    payment_method: str = Field(default="simulated")
    payment_status: str = Field(default="pending")
    order_date: Optional[datetime] = None
    notes: Optional[str] = None
    session_id: Optional[str] = None

    class Config:
        from_attributes = True


class CustomerOrderWithItems(CustomerOrderBase):
    """Customer order with items"""
    items: List[OrderItemBase] = []


class CheckoutRequest(BaseModel):
    """Checkout request model"""
    customer_info: CustomerInfo
    cart: Cart
    payment_method: str = Field(default="simulated")
