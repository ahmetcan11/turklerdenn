from typing import Any, List, Optional
from api import deps
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from starlette import status
from schemas.Free import free_schema
from models.free import Free as free_model
from models.user import User as user_model
from crud import crud_free
from utils.googleBucket import upload_business_profile_image, upload_free_item_images

router = APIRouter()


@router.post("/create")
def create_free_item(
    *,
    db: Session = Depends(deps.get_db),
    title: str = Form(...),
    address: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    city: str = Form(...),
    description: str = Form(...),
    images: List[UploadFile] = File(...),
    current_user: free_model = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new free item..
    """
    image_urls = upload_free_item_images(title, images)
    new_free_item = crud_free.crud_free_item.create_with_owner(
        db, obj_in=free_schema.FreeCreate(
            title=title,
            address=address,
            country=country,
            state=state,
            city=city,
            description=description,
        ), owner_id=current_user.id, image_urls=image_urls
    )
    return new_free_item


@router.get("/free_search")
def search(bl_latitude: float, bl_longitude: float, tr_latitude: float, tr_longitude: float, db: Session = Depends(deps.get_db),
           sort_by_view: bool = True, skip: int = 0,
    limit: int = 100,
           ):
    results = crud_free.crud_free_item.get_items_by_coordinates(
        db=db,
        bl_latitude=bl_latitude,
        bl_longitude=bl_longitude,
        tr_latitude=tr_latitude,
        tr_longitude=tr_longitude,
        skip=skip,
        limit=limit
    )

    return results


@router.delete("/deleteFreeItem")
def delete_free_item(
    free_item_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    free_item_check = crud_free.crud_free_item.get(db, id=free_item_id)
    if not free_item_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Free Item not found",
        )
    if free_item_check.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this free item",
        )
    deleted_free_item = crud_free.crud_free_item.remove(db, id=free_item_id)
    return deleted_free_item