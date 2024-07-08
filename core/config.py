import secrets

from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
import os, sys
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    PROJECT_NAME: str = "turk_api"
    API_V1_STR: str = "/api/v1"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgrespw"
    POSTGRES_DB: str = "app_db"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = "postgresql+psycopg2::us-west2:turklerdendb/.s.PGSQL.5432"
    BUSINESS_SECRET:str = "09d25e094faa6ca2556c818166b7a956"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost",
                                              "http://localhost:4200",
                                              "http://localhost:3000",
                                              "http://localhost:8080",
                                              "http://local.dockertoolbox.tiangolo.com",
                                              "http://192.168.0.105:3000",
                                              "http://localhost:63342",
                                              "https://fluent-horizon-388119.web.app/",
                                              "https://fluent-horizon-388119.web.app",
                                              "https://fluent-horizon-388119.firebaseapp.com",
                                              "https://turklerden.com",
                                              "http://turklerden.com",
                                              "https://www.turklerden.com",
                                              "http://www.turklerden.com"
                                              ]


    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True


settings = Settings()