from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette import status
from pymongo.errors import PyMongoError

from app.core.config import settings
from app.db.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, users, products, transactions, analytics, recommendations, forecasting, reviews, insights
from app.utils.responses import error_response
import json

app = FastAPI(
    title="Smart Retail Intelligence API",
    description="AI-powered retail analytics, recommendations, forecasting, and customer intelligence.",
    version="1.0.0",
)

# Backward-compatible alias for code that imports `api` directly.
api = app

def _normalize_origins(origins) -> list[str]:
    if origins is None:
        return ["*"]
    # If it's already a list/tuple, convert items to strings
    if isinstance(origins, (list, tuple, set)):
        return [str(o) for o in origins]
    # If it's a JSON string (from .env), try to parse
    if isinstance(origins, str):
        origins = origins.strip()
        if origins.startswith("["):
            try:
                parsed = json.loads(origins)
                if isinstance(parsed, (list, tuple)):
                    return [str(o) for o in parsed]
            except Exception:
                pass
        # single origin string
        return [origins]
    # Fallback
    try:
        return list(origins)  # type: ignore
    except Exception:
        return [str(origins)]

normalized_origins = _normalize_origins(settings.CORS_ORIGINS)

api.include_router(auth.router, prefix="/api/auth", tags=["auth"])
api.include_router(users.router, prefix="/api/users", tags=["users"])
api.include_router(products.router, prefix="/api/products", tags=["products"])
api.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
api.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
api.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
api.include_router(forecasting.router, prefix="/api/forecasting", tags=["forecasting"])
api.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
api.include_router(insights.router, prefix="/api/insights", tags=["insights"])

@api.on_event("startup")
async def startup_event() -> None:
    connect_to_mongo()

@api.on_event("shutdown")
async def shutdown_event() -> None:
    await close_mongo_connection()

@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    details = []
    for error in exc.errors():
        field_path = [str(part) for part in error.get("loc", []) if part != "body"]
        field = ".".join(field_path) or "request"
        details.append({"field": field, "message": error.get("msg", "Invalid value")})

    return JSONResponse(
        status_code=422,
        content=error_response("Please check the highlighted fields.", details),
    )

@api.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response("The server could not complete this request."),
    )

@api.exception_handler(PyMongoError)
async def database_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=error_response("Database is unavailable. Check your MongoDB connection and try again."),
    )

# Apply CORS middleware to the FastAPI app
api.add_middleware(
    CORSMiddleware,
    allow_origins=normalized_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
