from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Enum


class HouseType(str, Enum):
    SALE = "sale"
    RENT = "rent"


class HouseBase(BaseModel):
    title: str
    address: str
    country: str
    state: str
    city: str
    square_feet: Optional[int]  # Added square_feet field
    price: int
    house_type: HouseType


class HouseCreate(HouseBase):
    description: str


class House(HouseBase):
    id: int = None
    created_on: datetime = None
    owner_id: int = None

    class Config:
        orm_mode = True


