from claon_celery.celery import celery_client


@celery_client.task()
def test_task():
    pass
