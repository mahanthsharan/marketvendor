"""Product management routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid

from app.database import get_db
from app.models.models import Product, InventoryLevel, Channel
from app.schemas.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.utils.auth import get_current_seller
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/v1/products", tags=["products"])


@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Create new product"""
    # Check for duplicate SKU
    existing = db.query(Product).filter(
        and_(
            Product.seller_id == current_seller.seller_id,
            Product.sku == product_data.sku
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists for this seller"
        )
    
    product = Product(
        id=str(uuid.uuid4()),
        seller_id=current_seller.seller_id,
        sku=product_data.sku,
        name=product_data.name,
        description=product_data.description,
        category=product_data.category,
        base_price=product_data.base_price,
        current_price=product_data.base_price,
        cost=product_data.cost,
        weight=product_data.weight
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get product details"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Update product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.seller_id != current_seller.seller_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this product"
        )
    
    # Update fields
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.get("/seller/products", response_model=list)
async def list_seller_products(
    current_seller = Depends(get_current_seller),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all products for current seller"""
    products = db.query(Product).filter(
        Product.seller_id == current_seller.seller_id
    ).offset(skip).limit(limit).all()
    
    return products


@router.get("/search", response_model=list)
async def search_products(
    q: str = Query(..., min_length=1),
    category: str = Query(None),
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search for products"""
    query = db.query(Product).filter(Product.is_active == True)
    
    # Search by name or description
    query = query.filter(
        or_(
            Product.name.ilike(f"%{q}%"),
            Product.description.ilike(f"%{q}%")
        )
    )
    
    # Filter by category
    if category:
        query = query.filter(Product.category == category)
    
    # Filter by price range
    if min_price is not None:
        query = query.filter(Product.current_price >= min_price)
    if max_price is not None:
        query = query.filter(Product.current_price <= max_price)
    
    products = query.offset(skip).limit(limit).all()
    return products
