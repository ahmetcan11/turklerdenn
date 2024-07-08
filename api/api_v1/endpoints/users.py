from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette import status
from schemas.User import user_schema
from models.user import User as user_model
from crud import crud_user, crud_shared_room, crud_business, crud_business_image
from core.config import settings
from api import deps

router = APIRouter()


# USER
@router.get("/", response_model=List[user_schema.User], include_in_schema=False)
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    user_check = crud_user.user.get_multi(db, skip=skip, limit=limit)
    return user_check


@router.put("/me", response_model=user_schema.User, include_in_schema=False)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: str = Body(None),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = user_schema.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user_check = crud_user.user.update(db, db_obj=current_user, obj_in=user_in)
    return user_check


@router.get("/me", response_model=user_schema.User, include_in_schema=False)
def read_user_by_id(
    current_user: user_model = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user_id = current_user.id
    user = crud_user.user.get(db, id=user_id)
    if user == current_user and user.is_active == True:
        return user
    else:
        return {"is_active":False}


@router.put("/update", response_model=user_schema.User, include_in_schema=False)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: user_schema.UserUpdate,
    current_user: user_model = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user_id = current_user.id
    user = crud_user.user.get(db, id=user_id)
    if user != current_user:
        raise HTTPException(
            status_code=404,
            detail="You are not allowed to change another user's profile",
        )
    user_check = crud_user.user.update(db, db_obj=user, obj_in=user_in)
    return user_check


@router.delete("/deleteUser")
async def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    """
      Delete a user.
    """
    user_id = current_user.id
    user_check = crud_user.user.get(db, id=user_id)
    if current_user != user_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You can not delete another user",
        )
    deleted_user = crud_user.user.remove(db, id=current_user.id)
    return deleted_user


@router.delete("/deleteBusiness")
async def delete_business(
    *,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    """
      Delete a user.
    """
    user_id = current_user.id
    user_check = crud_user.user.get(db, id=user_id)
    if current_user != user_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You can not delete another user",
        )
    business_id = crud_business.business.get_by_owner_id(db, owner_id=user_id).id
    crud_business_image.delete_all(db, business_id=business_id)
    crud_business.business.delete_by_owner_id(db, owner_id=user_id)
    crud_user.user.delete(db, email=current_user.email)
    return {"Business Deleted"}


@router.get("/postList", include_in_schema=False)
async def post_list(
    *,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> List[dict]:
    """
    Get a list of posts.
    """
    user_check = crud_user.user.get(db, id=current_user.id)
    if not user_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get rooms for the owner
    rooms = crud_shared_room.shared_room.get_multi_by_owner(
        db=db, owner_id=current_user.id )

    # Create a list of JSON objects for the rooms and businesses
    results = []
    for room in rooms:
        room_dict = room.__dict__
        room_dict.pop("_sa_instance_state")
        results.append({"type": "room", "data": room_dict})

    return results