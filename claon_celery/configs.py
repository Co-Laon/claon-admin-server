from os import environ
from configparser import ConfigParser

config = ConfigParser(allow_no_value=True)

if environ.get("API_ENV") is None or environ.get("API_ENV") == "local":
    broker_url = "amqp://{user_name}:{password}@{ip}:{port}".format(
        user_name="claon_user",
        password="claon_password",
        ip="127.0.0.1",
        port="5672",
    )
elif environ.get("API_ENV") == "prod":
    try:
        with open("celery_config_prod.ini", encoding="utf-8") as file:
            config.read_file(file)
    except FileNotFoundError as e:
        raise FileNotFoundError("Please check config file by environment") from e

    broker_url = "amqp://{user_name}:{password}@{ip}:{port}".format(
        user_name=config.get("CELERY", "USER_NAME"),
        password=config.get("CELERY", "PASSWORD"),
        ip=config.get("CELERY", "IP"),
        port=config.get("CELERY", "PORT"),
    )
else:
    raise ValueError("Please check environment")
