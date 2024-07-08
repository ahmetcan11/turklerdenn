import os
from datetime import timedelta, datetime

import requests
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from starlette import status
from schemas.User import user_schema
from models.user import User as user_model
from crud import crud_user, crud_business, crud_shared_room, crud_free, crud_event, crud_house, crud_job
from api import deps
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
from enum import Enum
from fastapi import Query
from utils.updateViewsTask import update_views
from utils.googleAnalytics import write_unique_users_to_file

router = APIRouter()


@router.post("/updateViews")
def update_views(
    *,
    db: Session = Depends(deps.get_db),
    days_backward: int = Form(...),
    current_user: user_model = Depends(deps.get_current_active_superuser)
) -> Any:
    data = write_unique_users_to_file()
    return {"success": data}
