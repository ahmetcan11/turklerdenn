from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from starlette import status
from schemas.Housing import shared_room as room_schema
from schemas.User import user_schema
from models.user import User as user_model
from crud import crud_shared_room, crud_user
from api import deps
from utils.googleBucket import upload_shared_room

router = APIRouter()


@router.post("/create", response_model=room_schema.SharedRoom)
def create_room(
    *,
    db: Session = Depends(deps.get_db),
    title: str = Form(...),
    price: float = Form(...),
    address: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    city: str = Form(...),
    description: str = Form(...),
    furniture_available: bool = Form(...),
    images: List[UploadFile] = File(...),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new room.
    """

    image_urls = upload_shared_room(title, images)
    new_room = crud_shared_room.shared_room.create_with_owner(db, obj_in=room_schema.SharedRoomCreate(
            title=title,
            price=price,
            address=address,
            country=country,
            state=state,
            city=city,
            description=description,
            furniture_available=furniture_available
        ),
        owner_id=current_user.id,
        image_urls=image_urls)
    return new_room


@router.get("/user_room_list", response_model=List[room_schema.SharedRoom], include_in_schema=False)
def read_user_rooms(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve rooms.
    """
    if crud_user.user.is_superuser(current_user):
        rooms = crud_shared_room.shared_room.get_multi(db, skip=skip, limit=limit)
    else:
        rooms = crud_shared_room.shared_room.get_multi_by_owner(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return rooms


@router.delete("/deleteRoom", response_model=room_schema.SharedRoom)
def delete_room(
    room_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    room_check = crud_shared_room.shared_room.get(db, id=room_id)
    if not room_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    if room_check.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this room",
        )
    deleted_room = crud_shared_room.shared_room.remove(db, id=room_id)
    return deleted_room


@router.get("/getSharedRooms", include_in_schema=False)
def get_all_rooms_by_location(
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        db: Session = Depends(deps.get_db)):
    rooms = crud_shared_room.shared_room.get_rooms_by_location(
        db, country=country, state=state, city=city)
    return rooms
