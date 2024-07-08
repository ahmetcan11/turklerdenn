from typing import List, Optional
from pydantic import BaseModel


class GeneralBase(BaseModel):
    is_active: bool = True
    country: str
    state: str
    city: str
    address: Optional[str] = None
    post_id: Optional[str] = None
    description: Optional[str] = None
    interest: Optional[str] = None
    views: int = 0
    upvote: int = 0
    downvote: int = 0
    comments: Optional[List[str]] = None


class GeneralCreate(GeneralBase):
    pass


class GeneralUpdate(GeneralBase):
    pass


class General(GeneralBase):
    id: int
    owner_id: int
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    comment: Optional[str] = None


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    post_id: int

    class Config:
        orm_mode = True


class GeneralImageBase(BaseModel):
    image_url: str


class GeneralImageCreate(GeneralImageBase):
    pass


class GeneralImage(GeneralImageBase):
    id: int
    general_id: int

    class Config:
        orm_mode = True
