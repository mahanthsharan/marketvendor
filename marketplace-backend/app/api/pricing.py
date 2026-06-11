"""Dynamic pricing routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Product, PricingRule
from app.schemas.schemas import PricingRuleCreate, PricingRuleResponse
from app.utils.auth import get_current_seller
from app.services.pricing_service import DynamicPricingService
import uuid

router = APIRouter(prefix="/api/v1/pricing", tags=["pricing"])


@router.post("/{product_id}/rules", response_model=PricingRuleResponse)
async def create_pricing_rule(
    product_id: str,
    rule_data: PricingRuleCreate,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Create dynamic pricing rule for product"""
    # Verify product ownership
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product.seller_id != current_seller.seller_id:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate price range
    if rule_data.min_price > rule_data.max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price must be less than max_price"
        )
    
    rule = PricingRule(
        id=str(uuid.uuid4()),
        product_id=product_id,
        channel_id=rule_data.channel_id,
        min_price=rule_data.min_price,
        max_price=rule_data.max_price,
        demand_threshold_high=rule_data.demand_threshold_high,
        demand_threshold_low=rule_data.demand_threshold_low,
        price_increase_pct=rule_data.price_increase_pct,
        price_decrease_pct=rule_data.price_decrease_pct
    )
    
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return rule


@router.get("/{product_id}/rules", response_model=list)
async def list_pricing_rules(
    product_id: str,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Get pricing rules for product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product.seller_id != current_seller.seller_id:
        raise HTTPException(status_code=404, detail="Product not found")
    
    rules = db.query(PricingRule).filter(
        PricingRule.product_id == product_id
    ).all()
    
    return rules


@router.post("/{product_id}/recalculate-price")
async def recalculate_price(
    product_id: str,
    channel_id: str = None,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Recalculate and update product price based on demand"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product.seller_id != current_seller.seller_id:
        raise HTTPException(status_code=404, detail="Product not found")
    
    success = DynamicPricingService.update_price(db, product_id, channel_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to recalculate price"
        )
    
    # Refresh product to get updated price
    db.refresh(product)
    
    return {
        "message": "Price recalculated",
        "product_id": product_id,
        "new_price": product.current_price
    }


@router.get("/recommendations")
async def get_price_recommendations(
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Get price recommendations for all seller's products"""
    recommendations = DynamicPricingService.get_price_recommendations(
        db, current_seller.seller_id
    )
    
    return {
        "recommendations": recommendations,
        "count": len(recommendations)
    }


@router.get("/{product_id}/demand-score")
async def get_demand_score(
    product_id: str,
    channel_id: str = "all",
    db: Session = Depends(get_db)
):
    """Get current demand score for product"""
    demand_score = DynamicPricingService.calculate_demand_score(db, product_id, channel_id)
    
    interpretation = "low"
    if demand_score >= 0.8:
        interpretation = "high"
    elif demand_score >= 0.5:
        interpretation = "medium"
    
    return {
        "product_id": product_id,
        "channel_id": channel_id,
        "demand_score": round(demand_score, 2),
        "interpretation": interpretation
    }
