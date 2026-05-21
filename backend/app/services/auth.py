from datetime import datetime
from typing import Optional
from bson import ObjectId
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.db.database import get_collection
from app.utils.jwt import create_access_token, verify_access_token
from app.schemas.auth import RegisterRequest

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[dict]:
        collection = get_collection("users")
        user = await collection.find_one({"email": email})
        if not user or not AuthService.verify_password(password, user["password_hash"]):
            return None
        await collection.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.utcnow()}})
        roles = user.get("roles") or ["customer"]
        token = create_access_token(
            str(user["_id"]),
            {"roles": roles, "email": user.get("email"), "name": user.get("name")},
        )
        return {
            "access_token": token,
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "name": user.get("name"),
            "roles": roles,
        }

    @staticmethod
    async def register_user(payload: RegisterRequest):
        collection = get_collection("users")
        existing = await collection.find_one({"email": payload.email})
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        document = {
            "email": payload.email,
            "name": payload.name,
            "password_hash": AuthService.get_password_hash(payload.password),
            "roles": [payload.role if payload.role in {"customer", "admin"} else "customer"],
            "created_at": datetime.utcnow(),
        }
        return await collection.insert_one(document)

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
        try:
            payload = verify_access_token(token)
            roles = payload.get("roles")
            if not roles:
                try:
                    user = await get_collection("users").find_one({"_id": ObjectId(payload["sub"])})
                    roles = user.get("roles", ["customer"]) if user else ["customer"]
                except Exception:
                    roles = ["customer"]
            return {
                "user_id": payload["sub"],
                "roles": roles,
                "email": payload.get("email"),
                "name": payload.get("name"),
            }
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def get_current_user(user: dict = Depends(AuthService.get_current_user)) -> dict:
    return user
