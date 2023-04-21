from configparser import ConfigParser
from dataclasses import dataclass
from os import environ
from urllib.parse import quote

db_config = ConfigParser(allow_no_value=True)
try:
    with open("db_config_prod.ini") as file:
        db_config.read_file(file)
except FileNotFoundError:
    pass

redis_config = ConfigParser(allow_no_value=True)
try:
    with open("redis_config_prod.ini") as file:
        redis_config.read_file(file)
except FileNotFoundError:
    pass

config = ConfigParser(allow_no_value=True)
try:
    with open("{env}_config.ini".format(env=environ.get("API_ENV"))) as file:
        config.read_file(file)
except FileNotFoundError:
    if environ.get("API_ENV") != "test":
        raise FileNotFoundError("Please check config file by environment")


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
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"


@dataclass
class ProdConfig(Config):
    DEBUG: bool = False
    TEST_MODE: bool = False
    DB_ECHO: bool = True
    IP = db_config.get("DB", "IP", fallback="localhost")
    PORT = db_config.get("DB", "PORT", fallback="5432")
    DB_NAME = db_config.get("DB", "DB_NAME", fallback="claon_db")
    DB_USER_NAME = db_config.get("DB", "DB_USER_NAME", fallback="claon_user")
    DB_PASSWORD = db_config.get("DB", "DB_PASSWORD", fallback="claon_password")
    DB_URL: str = "postgresql+asyncpg://{user_name}:{password}@{ip}:{port}/{db_name}".format(
        user_name=DB_USER_NAME, password=quote(DB_PASSWORD), ip=IP, port=PORT, db_name=DB_NAME)
    REDIS_HOST: str = redis_config.get("REDIS", "REDIS_IP", fallback="localhost")
    REDIS_PORT: str = redis_config.get("REDIS", "REDIS_PORT", fallback="6379")


@dataclass
class TestConfig(Config):
    DEBUG: bool = True
    DB_ECHO: bool = True
    TEST_MODE: bool = True
    DB_URL: str = "sqlite+aiosqlite:///test.db"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"


def conf():
    config_dict = dict(prod=ProdConfig, local=LocalConfig, test=TestConfig)
    return config_dict[environ.get("API_ENV")]()
