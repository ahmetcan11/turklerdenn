from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class JobBase(BaseModel):
    title: str
    address: str
    country: str
    state: str
    city: str
    business_area: str
    work_type: str


class JobCreate(JobBase):
    description: str


class Job(JobBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
