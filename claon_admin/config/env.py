from configparser import ConfigParser
from os import environ

db_config = ConfigParser(allow_no_value=True)
redis_config = ConfigParser(allow_no_value=True)
config = ConfigParser(allow_no_value=True)

if environ.get("API_ENV") is None or environ.get("API_ENV") == "local":
    try:
        with open("local_config.ini") as file:
            config.read_file(file)
    except FileNotFoundError:
        raise FileNotFoundError("Please check config file by environment")
elif environ.get("API_ENV") == "test":
    pass
elif environ.get("API_ENV") == "prod":
    try:
        with open("prod_config.ini") as file:
            config.read_file(file)
        with open("redis_config_prod.ini") as file:
            redis_config.read_file(file)
        with open("db_config_prod.ini") as file:
            db_config.read_file(file)
    except FileNotFoundError:
        raise FileNotFoundError("Please check config file by environment")
else:
    raise ValueError("Please check environment")
