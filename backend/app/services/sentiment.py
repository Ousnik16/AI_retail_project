from app.db.database import get_collection
from transformers import pipeline

POSITIVE_WORDS = {"great", "excellent", "perfect", "fast", "smooth", "comfortable", "reliable", "strong"}
NEGATIVE_WORDS = {"bad", "poor", "slow", "warm", "broken", "weak", "late", "difficult"}


def _fallback_sentiment(text: str) -> dict:
    words = {word.strip(".,!?;:").lower() for word in text.split()}
    score = len(words & POSITIVE_WORDS) - len(words & NEGATIVE_WORDS)
    label = "POSITIVE" if score >= 0 else "NEGATIVE"
    return {"label": label, "score": 0.72 if label == "POSITIVE" else 0.68}


class SentimentService:
    @staticmethod
    async def analyze_reviews():
        collection = get_collection("reviews")
        cursor = collection.find({})
        reviews = []
        async for review in cursor:
            reviews.append(review)
        if not reviews:
            return {"sentiment": []}
        try:
            sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        except Exception:
            sentiment_pipeline = None
        results = []
        for review in reviews:
            analysis = sentiment_pipeline(review["review_text"][:512])[0] if sentiment_pipeline else _fallback_sentiment(review["review_text"])
            results.append({
                "product_id": review["product_id"],
                "review_id": str(review["_id"]),
                "label": analysis["label"],
                "score": analysis["score"],
            })
        return {"sentiment": results}
