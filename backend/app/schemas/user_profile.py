from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserProfileCreate(BaseModel):
    name: str
    age: int
    gender: str
    landHolding: str
    crop: str
    caste: str
    income: str


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    landHolding: Optional[str] = None
    crop: Optional[str] = None
    caste: Optional[str] = None
    income: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    landHolding: str
    crop: str
    caste: str
    income: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
