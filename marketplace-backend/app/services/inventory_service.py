"""
Inventory management service with concurrent update handling
Uses row-level locking to prevent race conditions
"""
import logging
from typing import Optional, Dict, List
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
import uuid

from app.models.models import InventoryLevel, Product, Channel, Order, OrderItem
from app.schemas.schemas import InventoryUpdate

logger = logging.getLogger(__name__)


class InventoryService:
    """Handles inventory operations with row-level locking"""
    
    @staticmethod
    def reserve_stock(
        db: Session,
        product_id: str,
        channel_id: str,
        quantity: int,
        order_id: str
    ) -> bool:
        """
        Reserve stock atomically using row-level locking.
        Returns True if successful, False if insufficient stock.
        """
        try:
            # Use SELECT ... FOR UPDATE to lock the row
            inventory = db.query(InventoryLevel).with_for_update().filter(
                and_(
                    InventoryLevel.product_id == product_id,
                    InventoryLevel.channel_id == channel_id
                )
            ).first()
            
            if not inventory:
                logger.warning(f"Inventory not found for product {product_id} on channel {channel_id}")
                return False
            
            if inventory.available_stock < quantity:
                logger.warning(
                    f"Insufficient stock for product {product_id}. "
                    f"Available: {inventory.available_stock}, Requested: {quantity}"
                )
                return False
            
            # Reserve the stock
            inventory.available_stock -= quantity
            inventory.reserved_stock += quantity
            
            db.commit()
            logger.info(f"Reserved {quantity} units of {product_id} on {channel_id} for order {order_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to reserve stock: {str(e)}")
            return False
    
    @staticmethod
    def release_reserved_stock(
        db: Session,
        product_id: str,
        channel_id: str,
        quantity: int,
        reason: str = "order_cancelled"
    ) -> bool:
        """Release reserved stock back to available"""
        try:
            inventory = db.query(InventoryLevel).with_for_update().filter(
                and_(
                    InventoryLevel.product_id == product_id,
                    InventoryLevel.channel_id == channel_id
                )
            ).first()
            
            if not inventory:
                return False
            
            if inventory.reserved_stock < quantity:
                logger.warning(f"Cannot release more stock than reserved")
                return False
            
            inventory.reserved_stock -= quantity
            inventory.available_stock += quantity
            db.commit()
            
            logger.info(f"Released {quantity} units of {product_id}. Reason: {reason}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to release stock: {str(e)}")
            return False
    
    @staticmethod
    def confirm_order(
        db: Session,
        product_id: str,
        channel_id: str,
        quantity: int
    ) -> bool:
        """
        Confirm order and remove from reserved stock permanently.
        Called when order is paid and confirmed.
        """
        try:
            inventory = db.query(InventoryLevel).with_for_update().filter(
                and_(
                    InventoryLevel.product_id == product_id,
                    InventoryLevel.channel_id == channel_id
                )
            ).first()
            
            if not inventory:
                return False
            
            if inventory.reserved_stock < quantity:
                logger.warning(f"Cannot confirm more than reserved")
                return False
            
            inventory.reserved_stock -= quantity
            inventory.total_stock = inventory.available_stock + inventory.reserved_stock
            db.commit()
            
            logger.info(f"Confirmed {quantity} units of {product_id} as sold")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to confirm order: {str(e)}")
            return False
    
    @staticmethod
    def update_inventory(
        db: Session,
        product_id: str,
        channel_id: str,
        total_stock: int,
        reason: str = "manual_update"
    ) -> bool:
        """Update total stock for a product on a channel"""
        try:
            inventory = db.query(InventoryLevel).with_for_update().filter(
                and_(
                    InventoryLevel.product_id == product_id,
                    InventoryLevel.channel_id == channel_id
                )
            ).first()
            
            if not inventory:
                # Create new inventory level
                inventory = InventoryLevel(
                    id=str(uuid.uuid4()),
                    product_id=product_id,
                    channel_id=channel_id,
                    available_stock=total_stock,
                    reserved_stock=0,
                    total_stock=total_stock
                )
                db.add(inventory)
            else:
                # Calculate new available stock
                # available = total - reserved
                new_available = total_stock - inventory.reserved_stock
                if new_available < 0:
                    logger.warning(
                        f"Cannot reduce total stock below reserved stock. "
                        f"Reserved: {inventory.reserved_stock}, New Total: {total_stock}"
                    )
                    return False
                
                inventory.available_stock = new_available
                inventory.total_stock = total_stock
            
            inventory.last_sync_status = "success"
            db.commit()
            
            logger.info(f"Updated inventory for {product_id}: total={total_stock}. Reason: {reason}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update inventory: {str(e)}")
            return False
    
    @staticmethod
    def get_inventory_status(db: Session, product_id: str) -> Dict:
        """Get inventory status across all channels"""
        inventories = db.query(InventoryLevel).filter(
            InventoryLevel.product_id == product_id
        ).all()
        
        status = {
            "product_id": product_id,
            "total_available": 0,
            "total_reserved": 0,
            "channels": {}
        }
        
        for inv in inventories:
            channel_name = db.query(Channel.name).filter(
                Channel.id == inv.channel_id
            ).scalar() or inv.channel_id
            
            status["channels"][channel_name] = {
                "available": inv.available_stock,
                "reserved": inv.reserved_stock,
                "total": inv.total_stock,
                "synced_at": inv.synced_at
            }
            status["total_available"] += inv.available_stock
            status["total_reserved"] += inv.reserved_stock
        
        return status
    
    @staticmethod
    def sync_across_channels(db: Session, product_id: str) -> bool:
        """
        Sync inventory across channels based on total available stock.
        Distributes stock proportionally across channels.
        """
        try:
            # Get total available stock across all channels
            total_available = db.query(
                func.sum(InventoryLevel.available_stock)
            ).filter(
                InventoryLevel.product_id == product_id
            ).scalar() or 0
            
            inventories = db.query(InventoryLevel).filter(
                InventoryLevel.product_id == product_id
            ).all()
            
            if not inventories:
                return False
            
            # For now, use a simple strategy: keep stock evenly distributed
            # In production, this would be more sophisticated
            stock_per_channel = total_available // len(inventories)
            remainder = total_available % len(inventories)
            
            for idx, inv in enumerate(inventories):
                inv_to_add = stock_per_channel + (1 if idx < remainder else 0)
                inv.available_stock = inv_to_add
                inv.total_stock = inv_to_add + inv.reserved_stock
            
            db.commit()
            logger.info(f"Synced inventory for product {product_id} across {len(inventories)} channels")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to sync inventory: {str(e)}")
            return False
