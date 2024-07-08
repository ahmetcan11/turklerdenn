from typing import Any, List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from starlette import status
from models.job import Job as job_model  # Import the Job model
from crud import crud_job  # Import the CRUD functions for jobs
from utils.googleBucket import upload_job  # Import the image upload function
from schemas.Job import job as job_schema  # Import the schema for jobs
from api import deps
from models.user import User as user_model

router = APIRouter()


@router.post("/create")
def create_job_post(
    *,
    db: Session = Depends(deps.get_db),
    title: str = Form(...),
    description: str = Form(...),
    images: List[UploadFile] = File(...),
    address: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    city: str = Form(...),
    business_area: str = Form(...),
    work_type: str = Form(...),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new job post.
    """
    image_urls = upload_job(title, images)
    new_job_post = crud_job.crud_job.create_with_owner(
        db,
        obj_in=job_schema.JobCreate(
            title=title,
            address=address,
            country=country,
            state=state,
            city=city,
            business_area=business_area,
            description=description,
            work_type=work_type,
        ),
        owner_id=current_user.id,
        image_urls=image_urls,
    )
    return new_job_post


@router.delete("/delete-job")
def delete_job_post(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    job_check = crud_job.crud_job.get(db, id=job_id)
    if not job_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job post not found",
        )
    if job_check.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this job_",
        )
    deleted_job_post = crud_job.crud_job.remove(db, id=job_id)
    return deleted_job_post
