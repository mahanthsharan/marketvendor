from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Enum, Index, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


class SellerStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class Seller(Base):
    __tablename__ = "sellers"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    business_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    phone = Column(String(20))
    status = Column(Enum(SellerStatus), default=SellerStatus.ACTIVE)
    commission_rate = Column(Float, default=0.15)  # 15% commission
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
    api_keys = relationship("SellerAPIKey", back_populates="seller", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_seller_email", "email"),
        Index("idx_seller_status", "status"),
    )


class SellerAPIKey(Base):
    __tablename__ = "seller_api_keys"
    
    id = Column(String(36), primary_key=True)
    seller_id = Column(String(36), ForeignKey("sellers.id"), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    seller = relationship("Seller", back_populates="api_keys")


class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # amazon, flipkart, ebay, own_store
    api_endpoint = Column(String(255))
    sync_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    inventory_levels = relationship("InventoryLevel", back_populates="channel")
    
    __table_args__ = (
        Index("idx_channel_name", "name"),
    )


class Product(Base):
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True)
    seller_id = Column(String(36), ForeignKey("sellers.id"), nullable=False)
    sku = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    base_price = Column(Float, nullable=False)  # Base price before demand adjustment
    current_price = Column(Float, nullable=False)  # Current price after dynamic adjustment
    cost = Column(Float)  # Cost to seller
    weight = Column(Float)  # in kg
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    seller = relationship("Seller", back_populates="products")
    inventory_levels = relationship("InventoryLevel", back_populates="product", cascade="all, delete-orphan")
    pricing_rules = relationship("PricingRule", back_populates="product", cascade="all, delete-orphan")
    demand_signals = relationship("DemandSignal", back_populates="product", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("seller_id", "sku", name="uq_seller_sku"),
        Index("idx_product_seller", "seller_id"),
        Index("idx_product_sku", "sku"),
        Index("idx_product_active", "is_active"),
    )


class InventoryLevel(Base):
    """Real-time inventory level per product per channel"""
    __tablename__ = "inventory_levels"
    
    id = Column(String(36), primary_key=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    channel_id = Column(String(36), ForeignKey("channels.id"), nullable=False)
    available_stock = Column(Integer, nullable=False, default=0)  # Currently available
    reserved_stock = Column(Integer, nullable=False, default=0)   # In pending orders
    total_stock = Column(Integer, nullable=False, default=0)      # Total (available + reserved)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())
    last_sync_status = Column(String(50), default="success")  # success, pending, failed
    
    # Relationships
    product = relationship("Product", back_populates="inventory_levels")
    channel = relationship("Channel", back_populates="inventory_levels")
    
    __table_args__ = (
        UniqueConstraint("product_id", "channel_id", name="uq_product_channel"),
        Index("idx_inventory_product", "product_id"),
        Index("idx_inventory_channel", "channel_id"),
        Index("idx_inventory_available", "available_stock"),
    )


class PricingRule(Base):
    """Dynamic pricing rules based on demand"""
    __tablename__ = "pricing_rules"
    
    id = Column(String(36), primary_key=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    channel_id = Column(String(36), ForeignKey("channels.id"))  # NULL = apply to all channels
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    demand_threshold_high = Column(Float, default=0.8)  # Increase price when >80% sold
    demand_threshold_low = Column(Float, default=0.2)   # Decrease price when <20% sold
    price_increase_pct = Column(Float, default=0.15)    # 15% increase at high demand
    price_decrease_pct = Column(Float, default=0.10)    # 10% decrease at low demand
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product", back_populates="pricing_rules")
    
    __table_args__ = (
        Index("idx_pricing_product", "product_id"),
    )


class DemandSignal(Base):
    """Track demand signals for pricing decisions"""
    __tablename__ = "demand_signals"
    
    id = Column(String(36), primary_key=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    channel_id = Column(String(36), ForeignKey("channels.id"), nullable=False)
    units_sold_24h = Column(Integer, default=0)
    units_viewed_24h = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    stock_utilization = Column(Float, default=0.0)  # % of stock sold
    demand_score = Column(Float, default=0.5)  # 0-1 scale
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    product = relationship("Product", back_populates="demand_signals")
    
    __table_args__ = (
        UniqueConstraint("product_id", "channel_id", name="uq_demand_product_channel"),
        Index("idx_demand_product", "product_id"),
    )


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    buyer_email = Column(String(255), nullable=False)
    seller_id = Column(String(36), ForeignKey("sellers.id"), nullable=False)
    channel_id = Column(String(36), ForeignKey("channels.id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, default=0)
    shipping = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    
    stripe_payment_intent_id = Column(String(255))
    
    # Shipping info
    shipping_address = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_order_seller", "seller_id"),
        Index("idx_order_status", "status"),
        Index("idx_order_payment_status", "payment_status"),
        Index("idx_order_created", "created_at"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(String(36), primary_key=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
