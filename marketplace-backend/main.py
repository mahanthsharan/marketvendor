"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from config import get_settings
from app.api import auth, products, inventory, orders, pricing, recommendations
from app.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Multi-vendor Marketplace with Real-time Inventory Sync and Dynamic Pricing"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
)


# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(pricing.router)
app.include_router(recommendations.router)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
