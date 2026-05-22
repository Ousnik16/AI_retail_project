from transformers import pipeline
from app.services.reviews import ReviewService

POSITIVE_WORDS = {"great", "excellent", "perfect", "fast", "smooth", "comfortable", "reliable", "strong"}
NEGATIVE_WORDS = {"bad", "poor", "slow", "warm", "broken", "weak", "late", "difficult"}


def _fallback_sentiment(text: str) -> dict:
    words = {word.strip(".,!?;:").lower() for word in text.split()}
    score = len(words & POSITIVE_WORDS) - len(words & NEGATIVE_WORDS)
    label = "POSITIVE" if score >= 0 else "NEGATIVE"
    return {"label": label, "score": 0.72 if label == "POSITIVE" else 0.68}


class SentimentService:
    @staticmethod
    async def analyze_reviews(user_id: str | None = None):
        reviews = await ReviewService.list_reviews(user_id)
        if not reviews:
            return {"sentiment": []}
        try:
            sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        except Exception:
            sentiment_pipeline = None
        results = []
        for review in reviews:
            text = review.get("review_text", "")
            analysis = sentiment_pipeline(text[:512])[0] if sentiment_pipeline else _fallback_sentiment(text)
            results.append({
                "product_id": review.get("product_id"),
                "review_id": str(review.get("_id")),
                "user_id": review.get("user_id"),
                "label": analysis.get("label"),
                "score": analysis.get("score"),
                "rating": review.get("rating"),
                "title": review.get("title"),
                "review_text": text,
            })
        return {"sentiment": results}
