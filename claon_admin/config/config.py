from os import path
from urllib.parse import quote

from claon_admin.config.env import config


class DatabaseConfig:
    def __init__(self):
        self.DDL_AUTO = config.get_by_key("sqlalchemy", {}).get_by_key("ddl-auto", "none")
        database_config = config.get_by_key("database", {})
        self.URL = "{driver}://{connect_info}/{db_name}".format(
            driver=database_config.get_by_key("driver"),
            connect_info="{user_name}:{password}@{host}:{port}".format(
                user_name=database_config.get_by_key("user"),
                password=quote(database_config.get_by_key("password")),
                host=database_config.get_by_key("host"),
                port=database_config.get_by_key("port")
            ) if database_config.get_by_key("host") is not None else "",
            db_name=database_config.get_by_key("name")
        ) if database_config else ""


class Config:
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    SESSION_SECRET_KEY = config.get_by_key("security", {}).get_by_key("session", {}).get_by_key("secret-key", "")
    BASE_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    HTML_DIR = BASE_DIR + "/claon_admin/template"

    DATABASE_CONFIG: DatabaseConfig = DatabaseConfig()
