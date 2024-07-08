from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class FreeBase(BaseModel):
    title: str
    address: str
    country: str
    state: str
    city: str


class FreeCreate(FreeBase):
    description: str


class Free(FreeBase):
    id: int = None
    created_on: datetime = None
    owner_id: int = None

    class Config:
        orm_mode = True
