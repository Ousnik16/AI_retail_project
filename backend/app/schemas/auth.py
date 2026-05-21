from pydantic import BaseModel, EmailStr

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str | None = None
    name: str | None = None
    email: EmailStr | None = None
    roles: list[str] = []

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = "customer"
