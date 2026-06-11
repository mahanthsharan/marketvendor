"""
Order processing service with payment integration
"""
import logging
import stripe
import uuid
from datetime import datetime, timedelta
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.models import Order, OrderItem, OrderStatus, PaymentStatus, Product
from app.services.inventory_service import InventoryService
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

stripe.api_key = settings.STRIPE_API_KEY


class OrderService:
    """Manages order creation, processing, and payment"""
    
    @staticmethod
    def create_order(
        db: Session,
        seller_id: str,
        channel_id: str,
        items_data: list,
        buyer_email: str,
        shipping_address: str
    ) -> dict:
        """
        Create order and reserve inventory atomically.
        Returns order details or error.
        """
        try:
            # Validate all items and calculate total
            order_items = []
            subtotal = 0.0
            
            for item_data in items_data:
                product = db.query(Product).filter(
                    and_(
                        Product.id == item_data["product_id"],
                        Product.seller_id == seller_id,
                        Product.is_active == True
                    )
                ).first()
                
                if not product:
                    return {
                        "success": False,
                        "error": f"Product {item_data['product_id']} not found"
                    }
                
                order_items.append({
                    "product": product,
                    "quantity": item_data["quantity"]
                })
                
                subtotal += product.current_price * item_data["quantity"]
            
            # Create order record
            order_id = str(uuid.uuid4())
            order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{order_id[:8]}"
            
            tax = subtotal * 0.18  # 18% GST
            shipping = 50.0  # Fixed shipping for now
            total_amount = subtotal + tax + shipping
            
            order = Order(
                id=order_id,
                order_number=order_number,
                buyer_email=buyer_email,
                seller_id=seller_id,
                channel_id=channel_id,
                subtotal=subtotal,
                tax=tax,
                shipping=shipping,
                total_amount=total_amount,
                shipping_address=shipping_address,
                status=OrderStatus.PENDING,
                payment_status=PaymentStatus.PENDING
            )
            
            db.add(order)
            db.flush()  # Get order ID for items
            
            # Reserve inventory for all items
            all_reserved = True
            for item_info in order_items:
                product = item_info["product"]
                quantity = item_info["quantity"]
                
                reserved = InventoryService.reserve_stock(
                    db, product.id, channel_id, quantity, order_id
                )
                
                if not reserved:
                    db.rollback()
                    return {
                        "success": False,
                        "error": f"Insufficient stock for {product.name}"
                    }
                
                # Create order item
                order_item = OrderItem(
                    id=str(uuid.uuid4()),
                    order_id=order_id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.current_price,
                    total_price=product.current_price * quantity
                )
                db.add(order_item)
            
            db.commit()
            
            logger.info(f"Order {order_number} created with {len(order_items)} items")
            
            return {
                "success": True,
                "order_id": order_id,
                "order_number": order_number,
                "total_amount": total_amount
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def create_payment_intent(db: Session, order_id: str) -> dict:
        """Create Stripe payment intent for order"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            
            if not order:
                return {"success": False, "error": "Order not found"}
            
            if order.payment_status != PaymentStatus.PENDING:
                return {"success": False, "error": "Order already has a payment in progress"}
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency="inr",
                metadata={
                    "order_id": order_id,
                    "order_number": order.order_number,
                    "seller_id": order.seller_id
                }
            )
            
            # Update order with payment intent ID
            order.stripe_payment_intent_id = intent.id
            order.payment_status = PaymentStatus.PROCESSING
            db.commit()
            
            logger.info(f"Payment intent created for order {order_id}")
            
            return {
                "success": True,
                "client_secret": intent.client_secret,
                "order_id": order_id,
                "amount": order.total_amount
            }
            
        except stripe.error.StripeError as e:
            db.rollback()
            logger.error(f"Stripe error: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create payment intent: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def confirm_payment(db: Session, order_id: str) -> dict:
        """Confirm payment and update order status"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            
            if not order:
                return {"success": False, "error": "Order not found"}
            
            # Verify payment with Stripe
            if order.stripe_payment_intent_id:
                intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
                
                if intent.status != "succeeded":
                    order.payment_status = PaymentStatus.FAILED
                    db.commit()
                    return {"success": False, "error": "Payment not successful"}
            
            # Mark reserved stock as confirmed (sold)
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            for item in order_items:
                InventoryService.confirm_order(
                    db, item.product_id, order.channel_id, item.quantity
                )
            
            # Update order status
            order.payment_status = PaymentStatus.COMPLETED
            order.status = OrderStatus.CONFIRMED
            db.commit()
            
            logger.info(f"Payment confirmed for order {order_id}")
            
            return {"success": True, "order_id": order_id}
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to confirm payment: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def cancel_order(db: Session, order_id: str) -> dict:
        """Cancel order and release reserved inventory"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            
            if not order:
                return {"success": False, "error": "Order not found"}
            
            if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
                return {"success": False, "error": "Cannot cancel shipped/delivered order"}
            
            # Release reserved inventory
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            for item in order_items:
                InventoryService.release_reserved_stock(
                    db, item.product_id, order.channel_id, item.quantity, "order_cancelled"
                )
            
            # Update order status
            order.status = OrderStatus.CANCELLED
            
            # Process refund if paid
            if order.payment_status == PaymentStatus.COMPLETED and order.stripe_payment_intent_id:
                refund = stripe.Refund.create(
                    payment_intent=order.stripe_payment_intent_id
                )
                order.payment_status = PaymentStatus.REFUNDED
            
            db.commit()
            
            logger.info(f"Order {order_id} cancelled")
            
            return {"success": True, "order_id": order_id}
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cancel order: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_seller_orders(db: Session, seller_id: str, status: str = None) -> list:
        """Get orders for a seller"""
        query = db.query(Order).filter(Order.seller_id == seller_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        return query.order_by(Order.created_at.desc()).all()
