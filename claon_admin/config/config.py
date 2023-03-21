from configparser import ConfigParser
from dataclasses import dataclass
from os import environ
from urllib.parse import quote

config = ConfigParser(allow_no_value=True)
try:
    with open("db_config_prod.ini") as file:
        config.read_file(file)
except FileNotFoundError:
    pass


@dataclass
class Config:
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


@dataclass
class LocalConfig(Config):
    DEBUG: bool = True
    DB_ECHO: bool = True
    TEST_MODE: bool = False
    IP = "localhost"
    PORT = "5432"
    DB_NAME = "claon_db"
    DB_USER_NAME = "claon_user"
    DB_PASSWORD = "claon_password"
    DB_URL: str = "postgresql+asyncpg://{user_name}:{password}@{ip}:{port}/{db_name}".format(
        user_name=DB_USER_NAME, password=quote(DB_PASSWORD), ip=IP, port=PORT, db_name=DB_NAME)


@dataclass
class ProdConfig(Config):
    DEBUG: bool = False
    TEST_MODE: bool = False
    DB_ECHO: bool = True
    IP = config.get("DB", "IP", fallback="localhost")
    PORT = config.get("DB", "PORT", fallback="5432")
    DB_NAME = config.get("DB", "DB_NAME", fallback="claon_db")
    DB_USER_NAME = config.get("DB", "DB_USER_NAME", fallback="claon_user")
    DB_PASSWORD = config.get("DB", "DB_PASSWORD", fallback="claon_password")
    DB_URL: str = "postgresql+asyncpg://{user_name}:{password}@{ip}:{port}/{db_name}".format(
        user_name=DB_USER_NAME, password=quote(DB_PASSWORD), ip=IP, port=PORT, db_name=DB_NAME)


@dataclass
class TestConfig(Config):
    DEBUG: bool = True
    DB_ECHO: bool = True
    TEST_MODE: bool = True
    DB_URL: str = "sqlite+aiosqlite:///test.db"


def conf():
    config_dict = dict(prod=ProdConfig, local=LocalConfig, test=TestConfig)
    return config_dict[environ.get("API_ENV")]()
