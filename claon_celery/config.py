from claon_celery.env import config


broker_url = "amqp://{user_name}:{password}@{ip}:{port}".format(
    user_name=config.get("celery.user"),
    password=config.get("celery.password"),
    ip=config.get("celery.host"),
    port=config.get("celery.port")
)
