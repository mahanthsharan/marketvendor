"""
Dynamic pricing service based on demand signals
Adjusts prices in real-time based on inventory levels and sales velocity
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
import math

from app.models.models import (
    Product, InventoryLevel, PricingRule, DemandSignal, 
    Order, OrderStatus, OrderItem
)

logger = logging.getLogger(__name__)


class DynamicPricingService:
    """Manages dynamic pricing based on demand"""
    
    @staticmethod
    def calculate_demand_score(db: Session, product_id: str, channel_id: str) -> float:
        """
        Calculate demand score (0-1) based on:
        - Stock utilization rate
        - Recent sales velocity
        - Conversion rate
        """
        # Get inventory levels
        inventory = db.query(InventoryLevel).filter(
            and_(
                InventoryLevel.product_id == product_id,
                InventoryLevel.channel_id == channel_id
            )
        ).first()
        
        if not inventory or inventory.total_stock == 0:
            return 0.5
        
        # Stock utilization rate
        stock_utilization = inventory.reserved_stock / max(inventory.total_stock, 1)
        
        # Recent sales (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(hours=24)
        recent_sales = db.query(func.sum(OrderItem.quantity)).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            and_(
                OrderItem.product_id == product_id,
                Order.created_at >= yesterday,
                Order.status != OrderStatus.CANCELLED
            )
        ).scalar() or 0
        
        # Get product base info
        product = db.query(Product).filter(Product.id == product_id).first()
        
        # Sales velocity score (how many sold recently)
        max_reasonable_sales = max(inventory.total_stock * 2, 10)
        sales_velocity = min(recent_sales / max_reasonable_sales, 1.0)
        
        # Weighted demand score
        # 50% stock utilization, 50% sales velocity
        demand_score = (stock_utilization * 0.5) + (sales_velocity * 0.5)
        
        return max(0.0, min(1.0, demand_score))
    
    @staticmethod
    def update_price(db: Session, product_id: str, channel_id: str = None) -> bool:
        """
        Update product price based on demand signals.
        If channel_id is None, updates base price (applied to all channels).
        """
        try:
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                logger.warning(f"Product {product_id} not found")
                return False
            
            # Get pricing rules
            query = db.query(PricingRule).filter(
                and_(
                    PricingRule.product_id == product_id,
                    PricingRule.is_active == True
                )
            )
            
            if channel_id:
                # Channel-specific pricing
                query = query.filter(
                    and_(
                        PricingRule.channel_id == channel_id,
                        PricingRule.channel_id.isnot(None)
                    )
                )
            else:
                # Base pricing (all channels)
                query = query.filter(PricingRule.channel_id.is_(None))
            
            pricing_rule = query.first()
            
            if not pricing_rule:
                logger.info(f"No pricing rule for product {product_id}")
                return False
            
            # Calculate demand score for the channel
            demand_score = DynamicPricingService.calculate_demand_score(
                db, product_id, channel_id or "all"
            )
            
            # Determine price adjustment
            new_price = product.base_price
            
            if demand_score >= pricing_rule.demand_threshold_high:
                # High demand - increase price
                increase_factor = 1 + pricing_rule.price_increase_pct
                new_price = product.base_price * increase_factor
                logger.info(
                    f"High demand for {product_id}: increasing price to {new_price:.2f} "
                    f"(demand_score: {demand_score:.2f})"
                )
            elif demand_score <= pricing_rule.demand_threshold_low:
                # Low demand - decrease price
                decrease_factor = 1 - pricing_rule.price_decrease_pct
                new_price = product.base_price * decrease_factor
                logger.info(
                    f"Low demand for {product_id}: decreasing price to {new_price:.2f} "
                    f"(demand_score: {demand_score:.2f})"
                )
            
            # Clamp price within min/max bounds
            new_price = max(pricing_rule.min_price, min(pricing_rule.max_price, new_price))
            
            # Update product price
            product.current_price = new_price
            
            # Update or create demand signal
            demand_signal = db.query(DemandSignal).filter(
                and_(
                    DemandSignal.product_id == product_id,
                    DemandSignal.channel_id == (channel_id or "all")
                )
            ).first()
            
            if not demand_signal:
                from app.models.models import DemandSignal
                import uuid
                demand_signal = DemandSignal(
                    id=str(uuid.uuid4()),
                    product_id=product_id,
                    channel_id=channel_id or "all",
                    demand_score=demand_score
                )
                db.add(demand_signal)
            else:
                demand_signal.demand_score = demand_score
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update price: {str(e)}")
            return False
    
    @staticmethod
    def get_price_recommendations(db: Session, seller_id: str) -> list:
        """Get price recommendations for all seller's products"""
        try:
            products = db.query(Product).filter(
                Product.seller_id == seller_id
            ).all()
            
            recommendations = []
            for product in products:
                demand_score = DynamicPricingService.calculate_demand_score(
                    db, product.id, "all"
                )
                
                pricing_rule = db.query(PricingRule).filter(
                    and_(
                        PricingRule.product_id == product.id,
                        PricingRule.is_active == True,
                        PricingRule.channel_id.is_(None)
                    )
                ).first()
                
                if pricing_rule:
                    recommended_price = product.current_price
                    action = "maintain"
                    
                    if demand_score >= pricing_rule.demand_threshold_high:
                        recommended_price = product.base_price * (1 + pricing_rule.price_increase_pct)
                        action = "increase"
                    elif demand_score <= pricing_rule.demand_threshold_low:
                        recommended_price = product.base_price * (1 - pricing_rule.price_decrease_pct)
                        action = "decrease"
                    
                    recommended_price = max(
                        pricing_rule.min_price,
                        min(pricing_rule.max_price, recommended_price)
                    )
                    
                    recommendations.append({
                        "product_id": product.id,
                        "product_name": product.name,
                        "current_price": product.current_price,
                        "recommended_price": recommended_price,
                        "action": action,
                        "demand_score": round(demand_score, 2)
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get price recommendations: {str(e)}")
            return []
