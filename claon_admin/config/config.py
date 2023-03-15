from configparser import ConfigParser
from dataclasses import dataclass
from os import environ
from urllib.parse import quote

if environ.get("API_ENV") == "prod":
    config = ConfigParser()
    with open("db_config_prod.ini") as file:
        config.read_file(file)


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
    IP = config.get("DB", "IP")
    PORT = config.get("DB", "PORT")
    DB_NAME = config.get("DB", "DB_NAME")
    DB_USER_NAME = config.get("DB", "DB_USER_NAME")
    DB_PASSWORD = config.get("DB", "DB_PASSWORD")
    DB_URL: str = "postgresql+asyncpg://{user_name}:{password}@{ip}:{port}/{db_name}".format(
        user_name=DB_USER_NAME, password=quote(DB_PASSWORD), ip=IP, port=PORT, db_name=DB_NAME)


@dataclass
class TestConfig(Config):
    TEST_MODE: bool = True


def conf():
    config = dict(prod=ProdConfig, local=LocalConfig, test=TestConfig)
    return config[environ.get("API_ENV")]()
