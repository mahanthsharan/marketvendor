"""Seller authentication routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models.models import Seller
from app.schemas.schemas import SellerRegister, SellerLogin, SellerResponse
from app.utils.auth import (
    get_password_hash, verify_password, create_access_token, get_current_seller
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=dict)
async def register(seller: SellerRegister, db: Session = Depends(get_db)):
    """Register new seller"""
    # Check if email already exists
    existing_seller = db.query(Seller).filter(Seller.email == seller.email).first()
    if existing_seller:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new seller
    new_seller = Seller(
        id=str(uuid.uuid4()),
        email=seller.email,
        password_hash=get_password_hash(seller.password),
        business_name=seller.business_name,
        contact_person=seller.contact_person,
        phone=seller.phone
    )
    
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    
    # Generate token
    access_token = create_access_token({"sub": new_seller.id})
    
    return {
        "message": "Seller registered successfully",
        "access_token": access_token,
        "seller": {
            "id": new_seller.id,
            "email": new_seller.email,
            "business_name": new_seller.business_name
        }
    }


@router.post("/login", response_model=dict)
async def login(credentials: SellerLogin, db: Session = Depends(get_db)):
    """Login seller"""
    seller = db.query(Seller).filter(Seller.email == credentials.email).first()
    
    if not seller or not verify_password(credentials.password, seller.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token({"sub": seller.id})
    
    return {
        "access_token": access_token,
        "seller": {
            "id": seller.id,
            "email": seller.email,
            "business_name": seller.business_name,
            "status": seller.status
        }
    }


@router.get("/me", response_model=SellerResponse)
async def get_current_user(
    current_seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Get current seller info"""
    seller = db.query(Seller).filter(Seller.id == current_seller.seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller
