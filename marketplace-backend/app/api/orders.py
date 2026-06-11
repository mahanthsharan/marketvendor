"""Order management routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.models import Order
from app.schemas.schemas import OrderCreate, OrderResponse, OrderItemResponse, PaymentIntentCreate
from app.utils.auth import get_current_seller
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    channel_id: str,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Create new order"""
    items = [
        {"product_id": item.product_id, "quantity": item.quantity}
        for item in order_data.items
    ]
    
    result = OrderService.create_order(
        db,
        current_seller.seller_id,
        channel_id,
        items,
        order_data.buyer_email,
        order_data.shipping_address
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    order = db.query(Order).filter(Order.id == result["order_id"]).first()
    return order


@router.get("/", response_model=list)
async def list_seller_orders(
    current_seller = Depends(get_current_seller),
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """List orders for current seller"""
    orders = OrderService.get_seller_orders(db, current_seller.seller_id, status_filter)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Get order details"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.seller_id != current_seller.seller_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


@router.post("/{order_id}/payment-intent", response_model=dict)
async def create_payment_intent(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Create Stripe payment intent for order"""
    result = OrderService.create_payment_intent(db, order_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result


@router.post("/{order_id}/confirm-payment")
async def confirm_payment(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Confirm payment and finalize order"""
    result = OrderService.confirm_payment(db, order_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"message": "Payment confirmed", "order_id": order_id}


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Cancel order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.seller_id != current_seller.seller_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    result = OrderService.cancel_order(db, order_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"message": "Order cancelled", "order_id": order_id}
