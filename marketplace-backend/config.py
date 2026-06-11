from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/marketplace"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Stripe
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "sk_test_xxxxx")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_xxxxx")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # App Settings
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Marketplace Engine"
    ALLOWED_CHANNELS: list = ["amazon", "flipkart", "own_store", "ebay"]
    
    # Inventory
    INVENTORY_SYNC_INTERVAL: int = 5  # seconds
    PRICING_UPDATE_INTERVAL: int = 60  # seconds
    
    # Dynamic Pricing
    DEMAND_HIGH_THRESHOLD: float = 0.8  # 80% stock sold
    DEMAND_LOW_THRESHOLD: float = 0.2   # 20% stock sold
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
