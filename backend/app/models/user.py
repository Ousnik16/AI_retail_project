from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List

class UserModel(BaseModel):
    id: str | None = Field(alias="_id")
    email: EmailStr
    name: str
    password_hash: str
    roles: List[str] = ["customer"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime | None = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "email": "jane.doe@example.com",
                "name": "Jane Doe",
                "password_hash": "hashed_password",
                "roles": ["customer"],
            }
        }
