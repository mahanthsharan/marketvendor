from typing import List, Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.models import Order, OrderItem, OrderStatus, Product


class RecommendationService:
    """Provides product recommendations based on order history and category."""

    @staticmethod
    def _top_products_query(
        db: Session,
        limit: int = 8,
        category: Optional[str] = None,
        exclude_ids: Optional[List[str]] = None,
    ) -> List[Product]:
        query = db.query(
            Product,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("sold_quantity"),
        ).outerjoin(
            OrderItem,
            OrderItem.product_id == Product.id,
        ).outerjoin(
            Order,
            and_(
                OrderItem.order_id == Order.id,
                Order.status != OrderStatus.CANCELLED,
            ),
        ).filter(
            Product.is_active == True,
        )

        if category:
            query = query.filter(Product.category == category)

        if exclude_ids:
            query = query.filter(Product.id.notin_(exclude_ids))

        query = query.group_by(Product.id)
        query = query.order_by(desc("sold_quantity"), desc(Product.created_at))
        query = query.limit(limit)

        results = query.all()
        return [product for product, _ in results]

    @staticmethod
    def get_recommendations(
        db: Session,
        product_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 8,
    ) -> List[Product]:
        if product_id:
            product = db.query(Product).filter(Product.id == product_id).first()
            if product and product.category:
                recommendations = RecommendationService._top_products_query(
                    db,
                    category=product.category,
                    exclude_ids=[product_id],
                    limit=limit,
                )
                if len(recommendations) >= limit:
                    return recommendations

                fallback = RecommendationService._top_products_query(
                    db,
                    limit=limit - len(recommendations),
                    exclude_ids=[product_id] + [p.id for p in recommendations],
                )
                return recommendations + fallback

        if category:
            return RecommendationService._top_products_query(
                db,
                category=category,
                limit=limit,
            )

        return RecommendationService._top_products_query(db, limit=limit)
