from typing import Literal

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

LOG_LEVEL_TYPE = Literal[
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]

ENVIRONMENT_TYPE = Literal["DEV", "PROD"]


class Config(BaseSettings):
    ENVIRONMENT: ENVIRONMENT_TYPE = "PROD"
    JWT_TOKEN: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    LOG_LEVEL: LOG_LEVEL_TYPE = "INFO"

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        dsn = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return PostgresDsn(dsn)


settings = Config()  # type: ignore
