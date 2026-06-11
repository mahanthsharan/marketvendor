"""Auth utilities and JWT handling"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class TokenData:
    def __init__(self, seller_id: str = None):
        self.seller_id = seller_id


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        seller_id: str = payload.get("sub")
        if seller_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(seller_id=seller_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_seller(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Dependency to get current authenticated seller"""
    return verify_token(credentials.credentials)
