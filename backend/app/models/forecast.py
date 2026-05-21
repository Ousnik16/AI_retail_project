from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class ForecastModel(BaseModel):
    id: str | None = Field(alias="_id")
    product_id: str
    date: datetime
    predicted_demand: float
    seasonality: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = {}

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
