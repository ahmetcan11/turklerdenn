from typing import Any, List, Optional
from api import deps
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from starlette import status
from schemas.Housing import house_schema
from models.house import House as house_model
from models.user import User as user_model
from crud import crud_house
from utils.googleBucket import upload_house

router = APIRouter()


@router.post("/create", response_model=house_schema.House)
def create_house(
    *,
    db: Session = Depends(deps.get_db),
    title: str = Form(...),
    address: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    city: str = Form(...),
    square_feet: Optional[int] = Form(None),  # Make square_feet optional with a default value of None
    price: float = Form(...),
    description: str = Form(...),
    house_type: house_schema.HouseType = Form(...),
    images: List[UploadFile] = File(...),
    current_user: house_model = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new house.
    """
    image_urls = upload_house(title, images)  # Implement your house image upload function

    new_house = crud_house.house.create_with_owner(
        db, obj_in=house_schema.HouseCreate(
            title=title,
            address=address,
            country=country,
            state=state,
            city=city,
            square_feet=square_feet,
            price=price,
            description=description,
            house_type=house_type
        ),
        owner_id=current_user.id, image_urls=image_urls
    )

    return new_house


@router.delete("/deleteHouse", response_model=house_schema.House)
def delete_house(
    house_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    house_check = crud_house.house.get(db, id=house_id)
    if not house_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="House not found",
        )
    if house_check.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this house",
        )
    deleted_house = crud_house.house.remove(db, id=house_id)
    return deleted_house
