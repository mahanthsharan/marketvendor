from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# ============ Seller Schemas ============

class SellerRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    business_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None


class SellerLogin(BaseModel):
    email: EmailStr
    password: str


class SellerResponse(BaseModel):
    id: str
    email: str
    business_name: str
    status: str
    commission_rate: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Product Schemas ============

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: float = Field(..., gt=0)
    cost: Optional[float] = None
    weight: Optional[float] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: str
    sku: str
    name: str
    description: Optional[str]
    category: Optional[str]
    base_price: float
    current_price: float
    cost: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Inventory Schemas ============

class InventoryLevelResponse(BaseModel):
    id: str
    product_id: str
    channel_id: str
    available_stock: int
    reserved_stock: int
    total_stock: int
    synced_at: datetime
    last_sync_status: str
    
    class Config:
        from_attributes = True


class InventoryUpdate(BaseModel):
    channel_id: str
    total_stock: int = Field(..., ge=0)
    reason: Optional[str] = None  # For audit trail


class BulkInventoryUpdate(BaseModel):
    updates: List[InventoryUpdate]


# ============ Order Schemas ============

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: str
    buyer_email: EmailStr


class OrderResponse(BaseModel):
    id: str
    order_number: str
    buyer_email: str
    status: str
    payment_status: str
    subtotal: float
    tax: float
    shipping: float
    total_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    quantity: int
    unit_price: float
    total_price: float
    
    class Config:
        from_attributes = True


# ============ Pricing Schemas ============

class PricingRuleCreate(BaseModel):
    channel_id: Optional[str] = None
    min_price: float = Field(..., gt=0)
    max_price: float = Field(..., gt=0)
    demand_threshold_high: float = Field(default=0.8, ge=0, le=1)
    demand_threshold_low: float = Field(default=0.2, ge=0, le=1)
    price_increase_pct: float = Field(default=0.15, ge=0, le=1)
    price_decrease_pct: float = Field(default=0.10, ge=0, le=1)


class PricingRuleResponse(BaseModel):
    id: str
    product_id: str
    channel_id: Optional[str]
    min_price: float
    max_price: float
    demand_threshold_high: float
    demand_threshold_low: float
    price_increase_pct: float
    price_decrease_pct: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Demand Signal Schemas ============

class DemandSignalResponse(BaseModel):
    id: str
    product_id: str
    channel_id: str
    units_sold_24h: int
    conversion_rate: float
    stock_utilization: float
    demand_score: float
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Payment Schemas ============

class PaymentIntentCreate(BaseModel):
    order_id: str


class PaymentIntentResponse(BaseModel):
    client_secret: str
    order_id: str
    amount: float


class PaymentWebhookEvent(BaseModel):
    type: str
    data: dict
