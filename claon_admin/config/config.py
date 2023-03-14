from dataclasses import dataclass
from os import environ
from urllib.parse import quote


@dataclass
class Config:
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


@dataclass
class LocalConfig(Config):
    DEBUG: bool = True
    DB_ECHO: bool = True
    TEST_MODE: bool = False
    DB_URL: str = "postgresql+asyncpg://{user_name}:{password}@localhost:5432/claon_db".format(
        user_name="claon_user", password=quote("claon_password"))


@dataclass
class ProdConfig(Config):
    DEBUG: bool = False
    TEST_MODE: bool = False
    DB_ECHO: bool = True
    DB_URL: str = "postgresql+asyncpg://{user_name}:{password}@localhost:5432/claon_db".format(
        user_name="claon_user", password=quote("claon_password"))


@dataclass
class TestConfig(Config):
    TEST_MODE: bool = True


def conf():
    config = dict(prod=ProdConfig, local=LocalConfig, test=TestConfig)
    return config[environ.get("API_ENV")]()
