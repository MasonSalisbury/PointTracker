from datetime import datetime
from pydantic import BaseModel, Field, validator

class Balance(BaseModel):
    payer: str = Field(..., description="Payer name")
    points: int = Field(..., description="Number of points")

class Transaction(BaseModel):
    payer: str = Field(..., description="Payer name")
    points: int = Field(..., description="Number of points")
    timestamp: datetime = Field(..., description="UTC timestamp of transaction time")

    @validator('payer')
    def payer_cannot_be_empty(cls, v: str):
        if not (v and v.strip()):
            raise ValueError("Payer name cannot be empty")
        return v

class Spend(BaseModel):
    points: int = Field(..., description="Number of points to spend")

    @validator('points')
    def points_cannot_be_positive(cls, v: int):
        if v < 1:
            raise ValueError("Points must be a positive nonzero number to spend")
        return v