from sqlalchemy.orm import Session
from crud import crud_user
from core.config import settings
from schemas.User import user_schema
from db import base  # noqa: F401
from sqlalchemy import create_engine, engine
# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    #Base.metadata.create_all(bind=engine)

    user = crud_user.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = user_schema.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud_user.user.create(db, obj_in=user_in)  # noqa: F841
