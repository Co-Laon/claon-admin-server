from celery import Celery
from claon_celery import config

celery_client = Celery(
    config_source=config
)
celery_client.conf.imports = ["claon_celery.tasks"]
