from datetime import datetime
from uuid import uuid4
from pymongo.errors import PyMongoError

from app.db.database import get_collection
from app.schemas.review import ReviewCreate

_fallback_reviews: list[dict] = []


class ReviewService:
    @staticmethod
    async def create_review(payload: ReviewCreate, user: dict) -> dict:
        document = {
            "user_id": user.get("email") or user.get("user_id"),
            "product_id": payload.product_id,
            "rating": payload.rating,
            "title": payload.title.strip(),
            "review_text": payload.review_text.strip(),
            "created_at": datetime.utcnow(),
        }

        try:
            result = await get_collection("reviews").insert_one(document)
            document["_id"] = result.inserted_id
            source = "mongo"
        except PyMongoError:
            document["_id"] = f"local-{uuid4().hex}"
            _fallback_reviews.append(document)
            source = "local-fallback"

        return {
            "id": str(document["_id"]),
            "user_id": document["user_id"],
            "product_id": document["product_id"],
            "rating": document["rating"],
            "title": document["title"],
            "review_text": document["review_text"],
            "created_at": document["created_at"].isoformat(),
            "source": source,
        }

    @staticmethod
    async def list_reviews(user_id: str | None = None) -> list[dict]:
        query = {}
        if user_id:
            query["user_id"] = user_id

        reviews = []
        try:
            cursor = get_collection("reviews").find(query)
            async for review in cursor:
                reviews.append(review)
        except PyMongoError:
            pass

        for review in _fallback_reviews:
            if user_id is None or review.get("user_id") == user_id:
                reviews.append(review)

        return reviews
