from os import environ, path
from urllib.parse import quote

from pydantic import BaseSettings

from claon_admin.config.env import config, db_config, redis_config


class Config(BaseSettings):
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    SESSION_SECRET_KEY = config.get("SESSION", "SECRET_KEY", fallback="")
    BASE_DIR: str = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    HTML_DIR: str = BASE_DIR + "/claon_admin/template"
    DB_DDL_AUTO: str = "none"


class LocalConfig(Config):
    DB_URL: str = "postgresql+asyncpg://{user_name}:{password}@{ip}:{port}/{db_name}".format(
        user_name="claon_user",
        password=quote("claon_password"),
        ip="localhost",
        port="5432",
        db_name="claon_db"
    )
    DB_DDL_AUTO: str = "none"
    REDIS_ENABLE: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"

    # JWT
    JWT_ALGORITHM = config.get("JWT", "ALGORITHM", fallback="")
    JWT_SECRET_KEY = config.get("JWT", "JWT_SECRET_KEY", fallback="")
    JWT_REFRESH_SECRET_KEY = config.get("JWT", "JWT_REFRESH_SECRET_KEY", fallback="")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(config.get("JWT", "ACCESS_TOKEN_EXPIRE_MINUTES", fallback="0"))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(config.get("JWT", "REFRESH_TOKEN_EXPIRE_MINUTES", fallback="0"))

    # GOOGLE OAUTH
    GOOGLE_CLIENT_ID = config.get("GOOGLE", "CLIENT_ID", fallback="")

    # AWS
    AWS_ENABLE: bool = True
    AWS_ACCESS_KEY_ID = config.get("AWS", "AWS_ACCESS_KEY_ID", fallback="")
    AWS_SECRET_ACCESS_KEY = config.get("AWS", "AWS_SECRET_ACCESS_KEY", fallback="")
    REGION_NAME = config.get("AWS", "REGION_NAME", fallback="")

    BUCKET = config.get("S3", "BUCKET", fallback="")


class ProdConfig(Config):
    DB_URL: str = "postgresql+asyncpg://{user_name}:{password}@{ip}:{port}/{db_name}".format(
        user_name=db_config.get("DB", "DB_USER_NAME", fallback=""),
        password=quote(db_config.get("DB", "DB_PASSWORD", fallback="")),
        ip=db_config.get("DB", "IP", fallback=""),
        port=db_config.get("DB", "PORT", fallback=""),
        db_name=db_config.get("DB", "DB_NAME", fallback="")
    )
    DB_DDL_AUTO: str = "none"
    REDIS_ENABLE: bool = True
    REDIS_HOST: str = redis_config.get("REDIS", "IP", fallback="")
    REDIS_PORT: str = redis_config.get("REDIS", "PORT", fallback="")

    # JWT
    JWT_ALGORITHM = config.get("JWT", "ALGORITHM", fallback="")
    JWT_SECRET_KEY = config.get("JWT", "JWT_SECRET_KEY", fallback="")
    JWT_REFRESH_SECRET_KEY = config.get("JWT", "JWT_REFRESH_SECRET_KEY", fallback="")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(config.get("JWT", "ACCESS_TOKEN_EXPIRE_MINUTES", fallback="0"))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(config.get("JWT", "REFRESH_TOKEN_EXPIRE_MINUTES", fallback="0"))

    # GOOGLE OAUTH
    GOOGLE_CLIENT_ID = config.get("GOOGLE", "CLIENT_ID", fallback="")

    # AWS
    AWS_ENABLE: bool = True
    AWS_ACCESS_KEY_ID = config.get("AWS", "AWS_ACCESS_KEY_ID", fallback="")
    AWS_SECRET_ACCESS_KEY = config.get("AWS", "AWS_SECRET_ACCESS_KEY", fallback="")
    REGION_NAME = config.get("AWS", "REGION_NAME", fallback="")

    BUCKET = config.get("S3", "BUCKET", fallback="")


class TestConfig(Config):
    DB_URL: str = "sqlite+aiosqlite:///test.db"
    DB_DDL_AUTO: str = "create"
    REDIS_ENABLE: bool = False
    AWS_ENABLE: bool = False


def conf():
    if environ.get("API_ENV") is None or environ.get("API_ENV") == "local":
        return LocalConfig()
    elif environ.get("API_ENV") == "test":
        return TestConfig()
    elif environ.get("API_ENV") == "prod":
        return ProdConfig()
    else:
        raise ValueError("Please check environment")
