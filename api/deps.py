from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from crud import crud_user
from schemas.Auth import token_schema
from models.user import User
from core import security
from core.config import settings
from db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login"
)

reusable_alternate_oauth3 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/alternate_login"
)
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db)
) -> User:
    user = crud_user.user.get(db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = token_schema.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud_user.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_alternate_user(
    db: Session = Depends(get_db), token: Optional[str] = Depends(reusable_alternate_oauth3)
) -> Optional[User]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = token_schema.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        empty_user = User()
        return empty_user
    user = crud_user.user.get(db, id=token_data.sub)
    if not user:
        empty_user = User()
        return empty_user
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not crud_user.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_alternate_user(
    current_user: Optional[User] = Depends(get_current_alternate_user),
) -> Optional[User]:
    if not crud_user.user.is_active(current_user):
        empty_user = User()
        return empty_user
    return current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not crud_user.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
