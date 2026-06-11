"""Database initialization with sample channels"""
from app.database import engine, SessionLocal, get_db_context, Base
from app.models.models import Channel
import uuid
import logging

logger = logging.getLogger(__name__)


def init_database():
    """Initialize database and create default channels"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Add default channels if they don't exist
    with get_db_context() as db:
        channels_data = [
            {"name": "amazon", "api_endpoint": "https://api.amazon.com"},
            {"name": "flipkart", "api_endpoint": "https://api.flipkart.com"},
            {"name": "own_store", "api_endpoint": "https://own-store.local"},
            {"name": "ebay", "api_endpoint": "https://api.ebay.com"}
        ]
        
        for channel_data in channels_data:
            existing = db.query(Channel).filter(
                Channel.name == channel_data["name"]
            ).first()
            
            if not existing:
                channel = Channel(
                    id=str(uuid.uuid4()),
                    name=channel_data["name"],
                    api_endpoint=channel_data["api_endpoint"],
                    sync_enabled=True
                )
                db.add(channel)
                logger.info(f"Created channel: {channel_data['name']}")
        
        db.commit()
    
    logger.info("Database initialization complete")


if __name__ == "__main__":
    init_database()
