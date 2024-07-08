from typing import Any, List, Optional
from api import deps
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from starlette import status
from models.general import General, GeneralImage, Comment
from schemas.General import general_schema
from models.general import General as general_model
from models.user import User as user_model
from crud import crud_general, crud_like
from utils.googleBucket import upload_general_images, upload_free_item_images
from enum import Enum
from pydantic import BaseModel


router = APIRouter()


class InterestType(str, Enum):
    IMMIGRATION = "immigration"
    TRAVEL = "travel"
    FOOD = "food"
    CARS = "cars"
    GROUP_CHATS = "group_chats"
    IT = "it"
    RANDOM = "random"
    FOOD_DELIVERY_APPS = "food_delivery_apps"
    E_COMMERCE = "e_commerce"


@router.post("/create")
def create_general(
    *,
    db: Session = Depends(deps.get_db),
    interest: InterestType = Form(None),
    country: str = Form(...),
    state: str = Form(...),
    city: str = Form(...),
    address: str = Form(None),
    description: str = Form(...),
    images: List[UploadFile] = File(None),
    current_user: general_model = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new general post...
    """
    image_urls = None
    if images:
        image_urls = upload_general_images(images)

    new_general = crud_general.crud_general.create_with_owner(
        db, obj_in=general_schema.GeneralCreate(
            country=country,
            state=state,
            city=city,
            address=address,
            description=description,
        ), owner_id=current_user.id, interest=interest, image_urls=image_urls
    )
    return new_general


@router.delete("/deleteGeneralPost")
def delete_general(
    general_id: int,
    db: Session = Depends(deps.get_db),
    current_user: general_model = Depends(deps.get_current_active_user),
) -> Any:
    general_check = crud_general.crud_general.get(db, id=general_id)
    if not general_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="General not found",
        )
    if general_check.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this general post",
        )
    deleted_general = crud_general.crud_general.remove(db, id=general_id)
    #deleted_general_images = crud_general.crud_general.ree
    return deleted_general


@router.post("/upvote/{general_post_id}")
def upvote_general_post(
    general_post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: general_model = Depends(deps.get_current_active_user)
):
    up_down_obj = crud_like.get_liked_general(db=db, user_id=current_user.id, general_post_id=general_post_id)
    if up_down_obj:
        if up_down_obj.downvote:
            # make downvote False in the updowngeneralpost table
            crud_like.remove_general_downvote(db=db, user_id=current_user.id, general_post_id=general_post_id)
            # Remove donvote number from general post
            crud_general.crud_general.remove_downvote_general_post(db=db,
                                                                         user_id=current_user.id,
                                                                         general_post_id=general_post_id)
    if not up_down_obj:
        crud_like.add_general_upvote(db=db, user_id=current_user.id, general_post_id=general_post_id)
        general_post = crud_general.crud_general.upvote_general_post(db=db,
                                                                     user_id=current_user.id,
                                                                     general_post_id=general_post_id)
        return general_post
    elif up_down_obj.upvote:
        crud_like.remove_general_upvote(db=db, user_id=current_user.id, general_post_id=general_post_id)
        general_post = crud_general.crud_general.remove_upvote_general_post(db=db,
                                                             user_id=current_user.id,
                                                             general_post_id=general_post_id)
        return general_post
    elif not up_down_obj.upvote:
        crud_like.add_general_upvote(db=db, user_id=current_user.id, general_post_id=general_post_id)
        general_post = crud_general.crud_general.upvote_general_post(db=db,
                                                             user_id=current_user.id,
                                                             general_post_id=general_post_id)
        return general_post
    else:
        crud_like.add_general_upvote(db=db, user_id=current_user.id, general_post_id=general_post_id)
        general_post = crud_general.crud_general.upvote_general_post(db=db,
                                                      user_id=current_user.id,
                                                      general_post_id=general_post_id)
        return general_post


@router.post("/downvote/{general_post_id}")
def downvote_general_post(
    general_post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: general_model = Depends(deps.get_current_active_user)
):
    up_down_obj = crud_like.get_liked_general(db=db, user_id=current_user.id, general_post_id=general_post_id)
    if up_down_obj:
        if up_down_obj.upvote:
            # make downvote False in the updowngeneralpost table
            crud_like.remove_general_upvote(db=db, user_id=current_user.id, general_post_id=general_post_id)
            # Remove donvote number from general post
            crud_general.crud_general.remove_upvote_general_post(db=db,
                                                                   user_id=current_user.id,
                                                                   general_post_id=general_post_id)
    if not up_down_obj:
        crud_like.add_general_downvote(db=db, user_id=current_user.id, general_post_id=general_post_id)
        general_post = crud_general.crud_general.downvote_general_post(db=db,
                                                                     user_id=current_user.id,
                                                                     general_post_id=general_post_id)
        return general_post
    elif up_down_obj.downvote:
        crud_like.remove_general_downvote(db=db, user_id=current_user.id, general_post_id=general_post_id)
        general_post = crud_general.crud_general.remove_downvote_general_post(db=db,
                                                                            user_id=current_user.id,
                                                                            general_post_id=general_post_id)
        return general_post
    elif not up_down_obj.downvote:
        crud_like.add_general_downvote(db=db, user_id=current_user.id, general_post_id=general_post_id)
        general_post = crud_general.crud_general.downvote_general_post(db=db,
                                                                     user_id=current_user.id,
                                                                     general_post_id=general_post_id)
        return general_post
    else:
        crud_like.add_general_downvote(db=db, user_id=current_user.id, general_post_id=general_post_id)
        general_post = crud_general.crud_general.downvote_general_post(db=db,
                                                                     user_id=current_user.id,
                                                                     general_post_id=general_post_id)
        return general_post
