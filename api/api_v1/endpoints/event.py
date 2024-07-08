from typing import Any, List, Optional
from api import deps
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from starlette import status

from crud import crud_user
from schemas.Event import event as event_schema  # Replace with your Event schema import
from models.event import Event as event_model  # Replace with your Event model import
from models.user import User as user_model
from crud.crud_event import crud_event  # Replace with your CRUD functions import
from utils.googleBucket import upload_event_images

router = APIRouter()


@router.post("/create")
def create_event(
    *,
    db: Session = Depends(deps.get_db),
    title: str = Form(...),
    address: str = Form(None),
    country: str = Form(None),
    state: str = Form(None),
    city: str = Form(None),
    start_time: str = Form(None),
    description: str = Form(None),
    online: bool = Form(None),
    price: float = Form(None),
    images: List[UploadFile] = File(...),
    current_user: event_model = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new event.
    time format example: 2023-09-03T12:00:00Z
    """
    image_urls = upload_event_images(title, images)

    new_event = crud_event.create_with_owner(
        db, obj_in=event_schema.EventCreate(
            title=title,
            address=address,
            country=country,
            state=state,
            city=city,
            start_time=start_time,
            description=description,
            online=online,
            price=price,
        ),
        owner_id=current_user.id,
        image_urls=image_urls
    )
    return new_event


@router.delete("/deleteEvent")
def delete_event(
    event_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    event_check = crud_event.get(db, id=event_id)
    if not event_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    if event_check.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this event",
        )
    deleted_event = crud_event.remove(db, id=event_id)
    return deleted_event
