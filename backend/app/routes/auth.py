from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, RegisterRequest, TokenSchema
from app.services.auth import AuthService
from app.utils.responses import success_response

router = APIRouter()

@router.post("/login", response_model=TokenSchema)
async def login(payload: LoginRequest):
    auth = await AuthService.authenticate_user(payload.email, payload.password)
    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenSchema(**auth)

@router.post("/register")
async def register(payload: RegisterRequest):
    user = await AuthService.register_user(payload)
    return success_response("User registered successfully", {"user_id": str(user.inserted_id)})
