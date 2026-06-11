"""Product recommendation routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import ProductResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.get("/", response_model=list[ProductResponse])
async def get_recommendations(
    product_id: str | None = Query(None),
    category: str | None = Query(None),
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Get recommended products."""
    recommendations = RecommendationService.get_recommendations(
        db,
        product_id=product_id,
        category=category,
        limit=limit,
    )
    return recommendations
