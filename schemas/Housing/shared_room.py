from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True


class SharedRoom(OurBaseModel):
    title: str
    price: str
    address: str
    country: str
    state: str
    city: str
    description: str
    furniture_available: Optional[bool] = False


class SharedRoomCreate(SharedRoom):
    title: str


class SharedRoomUpdate(SharedRoom):
    pass


class SharedRoomInDB(SharedRoom):
    id: int

    class Config:
        orm_mode = True

