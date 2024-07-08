from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class Event(BaseModel):
    title: str
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    start_time: Optional[datetime] = None


class EventCreate(Event):
    description: Optional[str] = None
    online: Optional[bool] = False
    price: Optional[str] = None



class EventUpdate(Event):
    pass


class EventBase(Event):
    pass

