from celery import Celery
from claon_celery import configs

celery_client = Celery(
    config_source=configs
)
celery_client.conf.imports = ["claon_celery.tasks"]
