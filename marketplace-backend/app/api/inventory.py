"""Inventory management routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models.models import InventoryLevel, Product, Channel
from app.schemas.schemas import InventoryUpdate, InventoryLevelResponse
from app.utils.auth import get_current_seller
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


@router.post("/{product_id}/initialize")
async def initialize_inventory(
    product_id: str,
    channel_id: str,
    initial_stock: int,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Initialize inventory for a product on a channel"""
    # Verify product ownership
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product.seller_id != current_seller.seller_id:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify channel exists
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if inventory already exists
    existing = db.query(InventoryLevel).filter(
        InventoryLevel.product_id == product_id,
        InventoryLevel.channel_id == channel_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory already initialized for this product-channel"
        )
    
    # Create inventory level
    inventory = InventoryLevel(
        id=str(uuid.uuid4()),
        product_id=product_id,
        channel_id=channel_id,
        available_stock=initial_stock,
        reserved_stock=0,
        total_stock=initial_stock
    )
    
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    
    return {
        "message": "Inventory initialized",
        "inventory": {
            "available": inventory.available_stock,
            "reserved": inventory.reserved_stock,
            "total": inventory.total_stock
        }
    }


@router.put("/{product_id}/update")
async def update_inventory(
    product_id: str,
    inventory_data: InventoryUpdate,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Update inventory for a product"""
    # Verify product ownership
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product.seller_id != current_seller.seller_id:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update inventory
    success = InventoryService.update_inventory(
        db,
        product_id,
        inventory_data.channel_id,
        inventory_data.total_stock,
        inventory_data.reason or "manual_update"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update inventory"
        )
    
    # Get updated inventory
    inventory = db.query(InventoryLevel).filter(
        InventoryLevel.product_id == product_id,
        InventoryLevel.channel_id == inventory_data.channel_id
    ).first()
    
    return {
        "message": "Inventory updated",
        "inventory": {
            "available": inventory.available_stock,
            "reserved": inventory.reserved_stock,
            "total": inventory.total_stock
        }
    }


@router.get("/{product_id}/status")
async def get_inventory_status(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get inventory status for a product across all channels"""
    status = InventoryService.get_inventory_status(db, product_id)
    return status


@router.get("/{product_id}/channels", response_model=list)
async def get_product_inventory_by_channel(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get inventory for a product on all channels"""
    inventories = db.query(InventoryLevel).filter(
        InventoryLevel.product_id == product_id
    ).all()
    
    result = []
    for inv in inventories:
        channel = db.query(Channel).filter(Channel.id == inv.channel_id).first()
        result.append({
            "channel_id": inv.channel_id,
            "channel_name": channel.name if channel else inv.channel_id,
            "available": inv.available_stock,
            "reserved": inv.reserved_stock,
            "total": inv.total_stock,
            "synced_at": inv.synced_at
        })
    
    return result


@router.post("/{product_id}/sync-channels")
async def sync_inventory_across_channels(
    product_id: str,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Sync inventory across channels for a product"""
    # Verify product ownership
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product.seller_id != current_seller.seller_id:
        raise HTTPException(status_code=404, detail="Product not found")
    
    success = InventoryService.sync_across_channels(db, product_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to sync inventory"
        )
    
    status = InventoryService.get_inventory_status(db, product_id)
    return {
        "message": "Inventory synced across channels",
        "inventory_status": status
    }
