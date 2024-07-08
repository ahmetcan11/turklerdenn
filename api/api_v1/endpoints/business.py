from datetime import timedelta
from typing import Any, List, Optional
import sqlalchemy
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from starlette import status
from schemas.Business import business_schema
from schemas.User import user_schema
from models.user import User as user_model
from models.business import BusinessRequest
from schemas.Business.business_schema import BusinessUpdate, PlaceRequest, UpdateRequestStatus

from crud import crud_business, crud_user, crud_business_image
from api import deps
from utils.googleBucket import upload_business_profile_image
from utils.common_util import validate_phone_number, get_business_details, get_photo

router = APIRouter()


def create_business(db, business_in: business_schema.BusinessCreateNoUser
, images: Optional[List[UploadFile]] = File(None)) -> bool:
    """
    Create new business.
    """
    try:
        # Create the user and business and Upload the file to Google Cloud Storage
        if images:
            image_urls = upload_business_profile_image(str(business_in.name), images)
            new_user = crud_user.user.create_with_business(db, obj_in=business_in, image_urls=image_urls)
        else:
            new_user = crud_user.user.create_with_business(db, obj_in=business_in, image_urls=["empty"])
        return {new_user}
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()  # Rollback the transaction in case of a database error
        if "unique constraint" in str(e):
            raise HTTPException(status_code=400, detail="Unique Constraint, unique key already exists!")
        else:
            raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        # Handle other exceptions (e.g., image upload error)
        if hasattr(e, "detail"):
            detail = e.detail
        else:
            detail = "An error occurred." + str(e)
        raise HTTPException(status_code=500, detail=detail)

@router.post("/requestToAddBusiness")
async def request_place(place_request: PlaceRequest, 
                        db: Session = Depends(deps.get_db)
                        ):
    place_id = place_request.place_id
    description = place_request.description
    request = crud_business.business.check_business_add_request(db, place_id)
    
    if request:
        return {"message": "This business request has been made already.", "approved": request.approved_status}
    else:
        new_request = crud_business.business.create_business_add_request(db, place_id, description)
        return {"message": "We are reviewing the request.", "approved": new_request.approved_status}
    
@router.post("/verifyBusiness")
async def approve_place(update_request: business_schema.BusinessApprove = Form(...),
                        place_id:str = Form(...),
                        category_list: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_superuser)):
    approved_status = update_request
    # Create the business here
    # Call get_business_details from the common_util.py file
    # and create the business with the details
    # Call the get_photo method drom the common_util.py file
    # and upload the photo to the google cloud storage
    try:
        if approved_status == "approved":
            business_details = get_business_details(place_id)
            if business_details:
                photo_urls = get_photo(place_id)
                image_urls = photo_urls if photo_urls else ["empty"]
                new_business = crud_business.business.create_business_without_owner(
                    db, obj_in=business_schema.BusinessCreate(
                    name=business_details['name'],
                    is_online=False,
                    address=business_details['address'],
                    country=business_details['country'],
                    state=business_details['state'],
                    city=business_details['city'],
                    website=business_details['website'],
                    tel_number=business_details['tel_number'],
                    rating=business_details['rating'],
                    user_rating_count=business_details['user_rating_count'],
                    place_id=business_details['place_id'],
                    category_list=category_list,
                    ),
                    image_urls=image_urls
                )
            request = crud_business.business.update_business_request(db, place_id, approved_status)
            if not request:
                raise HTTPException(status_code=404, detail="Request not found")
            return {
                "new_business": new_business
            }
        elif approved_status == "declined":
            request = crud_business.business.update_business_request(db, place_id, approved_status)
            if not request:
                raise HTTPException(status_code=404, detail="Request not found")
            return {
                "approved_status": request.approved_status
            }
            
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()  # Rollback the transaction in case of a database error
        if "unique constraint" in str(e):
            raise HTTPException(status_code=400, detail="Unique Constraint, unique key already exists!")
        else:
            raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        # Handle other exceptions (e.g., image upload error)
        if hasattr(e, "detail"):
            detail = e.detail
        else:
            detail = "An error occurred." + str(e)
        raise HTTPException(status_code=500, detail=detail)
         
    

@router.post("/addBusinessNoUser", response_model_exclude={"hashed_password","is_superuser","created_on"})
def business_registration(
        name: str = Form(...),
        is_online: bool = Form(None),
        address: str = Form(...),
        country: str = Form(...),
        state: str = Form(...),
        city: str = Form(...),
        category_list: str = Form(...),
        description: str = Form(None),
        website: str = Form(None),
        tel_number: str = Form(None),
        whatsapp_number: str = Form(None),
        images: Optional[List[UploadFile]] = File(None),
        db: Session = Depends(deps.get_db),
        current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    
    try:
        if images:
            # Create the user and business and Upload the file to Google Cloud Storage
            image_urls = upload_business_profile_image(str(name), images)
            new_business = crud_business.business.create_business_without_owner(
                db, obj_in=business_schema.BusinessCreate(
                name=name,
                is_online=is_online,
                address=address,
                country=country,
                state=state,
                city=city,
                category_list=category_list,
                description=description,
                website=website,
                tel_number=tel_number,
                whatsapp_number=whatsapp_number,
            ),
            image_urls=image_urls
            )
        else:
            new_business = crud_business.business.create_business_without_owner(
                db, obj_in=business_schema.BusinessCreate(
                    name=name,
                    is_online=is_online,
                    address=address,
                    country=country,
                    state=state,
                    city=city,
                    category_list=category_list,
                    description=description,
                    website=website,
                    tel_number=tel_number,
                    whatsapp_number=whatsapp_number,
                ),
                image_urls=["empty"])
        return {
            "business_id": new_business.id,
        }
            
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()  # Rollback the transaction in case of a database error
        if "unique constraint" in str(e):
            raise HTTPException(status_code=400, detail="Unique Constraint, unique key already exists!")
        else:
            raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        # Handle other exceptions (e.g., image upload error)
        if hasattr(e, "detail"):
            detail = e.detail
        else:
            detail = "An error occurred." + str(e)
        raise HTTPException(status_code=500, detail=detail)


        
@router.post("/addBusiness", response_model_exclude={"hashed_password","is_superuser","created_on"})
def business_registration(
        name: str = Form(...),
        is_online: bool = Form(None),
        address: str = Form(...),
        country: str = Form(...),
        state: str = Form(...),
        city: str = Form(...),
        category_list: str = Form(...),
        description: str = Form(None),
        website: str = Form(None),
        tel_number: str = Form(None),
        whatsapp_number: str = Form(None),
        images: Optional[List[UploadFile]] = File(None),
        db: Session = Depends(deps.get_db),
        current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    if tel_number and len(tel_number) <= 4:  # Assuming country codes are 3 digits max
        tel_number = None
    if whatsapp_number and len(whatsapp_number) <= 4:  # Assuming country codes are 3 digits max
        whatsapp_number = None
    # Validate phone numbers
    if tel_number:
        validate_phone_number(tel_number)
    if whatsapp_number:
        validate_phone_number(whatsapp_number)
    existing_user = crud_user.user.get_by_email(db, email=current_user.email)
    try:
        if existing_user:
            if existing_user.is_active:
                 ## Add business to the user
                 if images:
                     # Create the user and business and Upload the file to Google Cloud Storage
                     image_urls = upload_business_profile_image(str(name), images)
                     new_business = crud_business.business.create_business_with_owner(
                         db, obj_in=business_schema.BusinessCreate(
                         name=name,
                         is_online=is_online,
                         address=address,
                         country=country,
                         state=state,
                         city=city,
                         category_list=category_list,
                         description=description,
                         website=website,
                         tel_number=tel_number,
                         whatsapp_number=whatsapp_number,
                     ),
                     owner_id=current_user.id,
                     image_urls=image_urls
                     )
                 else:
                     new_business = crud_business.business.create_business_with_owner(
                         db, obj_in=business_schema.BusinessCreate(
                             name=name,
                             is_online=is_online,
                             address=address,
                             country=country,
                             state=state,
                             city=city,
                             category_list=category_list,
                             description=description,
                             website=website,
                             tel_number=tel_number,
                             whatsapp_number=whatsapp_number,
                         ),
                         owner_id=current_user.id,
                         image_urls=["empty"])
                 return {
                     "business_id": new_business.id,
                 }
            else:
                raise HTTPException(status_code=403, detail="User is not active, please verify the user.")
        else:
            raise HTTPException(status_code=404, detail="User not found.")
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()  # Rollback the transaction in case of a database error
        if "unique constraint" in str(e):
            raise HTTPException(status_code=400, detail="Unique Constraint, unique key already exists!")
        else:
            raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        # Handle other exceptions (e.g., image upload error)
        if hasattr(e, "detail"):
            detail = e.detail
        else:
            detail = "An error occurred." + str(e)
        raise HTTPException(status_code=500, detail=detail)


@router.delete("/deleteBusiness", response_model=business_schema.Business)
def read_items(
    business_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    user_id = current_user.id
    user_check = crud_user.user.get(db, id=user_id)
    if current_user != user_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Authorized",
        )
    business_check = crud_business.business.get(db, id=business_id)
    if not business_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
    deleted_business = crud_business.business.remove(db, id=business_id)
    return deleted_business


@router.put("/{business_id}", include_in_schema=False)  # Update with your actual response schema
def update_business2(
    business_id: int,
    business_update: business_schema.BusinessUpdate,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user)
):
    user_id = current_user.id
    user_check = crud_user.user.get(db, id=user_id)
    if current_user != user_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Authorized",
        )
    business_check = crud_business.business.get(db, id=business_id)
    if not business_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
    # Update the business with the new data
    db_business = crud_business.business.update(db=db, db_obj=business_check, obj_in=business_update)
    return db_business


@router.post("/updateProfile")  # Update with your actual response schema
def update_business(
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    user_tel_number: Optional[str] = Form(None),
    user_whatsapp_number: Optional[str] = Form(None),
    business_id: int = Form(None),
    name: Optional[str] = Form(None),
    is_online: Optional[bool] = Form(None),
    address: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    category_list: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    business_tel_number: Optional[str] = Form(None),
    business_whatsapp_number: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user)
):
    user_id = current_user.id
    user_check = crud_user.user.get(db, id=user_id)
    if current_user != user_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Authorized",
        )
        # Create a dictionary of non-None values
    user_obj_in_data = {
        "first_name": first_name,
        "last_name": last_name,
        "tel_number": user_tel_number,
        "whatsapp_number": user_whatsapp_number,
    }

    # Remove keys with None values from the dictionary
    obj_in_data = {k: v for k, v in user_obj_in_data.items() if v is not None}

    db_user = crud_user.user.update(
        db=db,
        db_obj=user_check,
        obj_in=user_schema.UserUpdate(**obj_in_data)
    )
    user_public = {
        "id": db_user.id,
        "email": db_user.email,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "tel_number": db_user.tel_number,
        "whatsapp_number": db_user.whatsapp_number
    }
    if business_id:
        business_check = crud_business.business.get(db, id=business_id)
        if business_check.owner_id != db_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't own business",
            )
        if not business_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found",
            )

        # Create a dictionary of non-None values
        obj_in_data = {
            "name": name,
            "is_online": is_online,
            "address": address,
            "country": country,
            "state": state,
            "city": city,
            "category_list": category_list,
            "description": description,
            "website": website,
            "tel_number": business_tel_number,
            "whatsapp_number": business_whatsapp_number,
        }

        # Remove keys with None values from the dictionary
        obj_in_data = {k: v for k, v in obj_in_data.items() if v is not None}
        # Update the business with the new data
        if images:
            # Create the user and business and Upload the file to Google Cloud Storage
            image_urls = upload_business_profile_image(str(name), images)
            obj_in_data["images"] = image_urls  # Add the image URLs to the dictionary
            crud_business_image.update_image_url(db, business_id, image_urls[0])
        db_business = crud_business.business.update(
            db=db,
            db_obj=business_check,
            obj_in=business_schema.BusinessUpdate(**obj_in_data)
        )

        return {
            "db_business": db_business,
            "db_business_image": db_business.images,
            "user_public": user_public,
        }

    return {
        "user_public": user_public,
    }
