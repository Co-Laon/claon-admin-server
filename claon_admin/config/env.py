from configparser import ConfigParser
from os import environ

db_config = ConfigParser(allow_no_value=True)
redis_config = ConfigParser(allow_no_value=True)
config = ConfigParser(allow_no_value=True)

if environ.get("API_ENV") is None or environ.get("API_ENV") == "local":
    try:
        with open("local_config.ini", encoding="utf-8") as file:
            config.read_file(file)
    except FileNotFoundError as e:
        raise FileNotFoundError("Please check config file by environment") from e
elif environ.get("API_ENV") == "test":
    pass
elif environ.get("API_ENV") == "prod":
    try:
        with open("prod_config.ini", encoding="utf-8") as file:
            config.read_file(file)
        with open("redis_config_prod.ini", encoding="utf-8") as file:
            redis_config.read_file(file)
        with open("db_config_prod.ini", encoding="utf-8") as file:
            db_config.read_file(file)
    except FileNotFoundError as e:
        raise FileNotFoundError("Please check config file by environment") from e
else:
    raise ValueError("Please check environment")
