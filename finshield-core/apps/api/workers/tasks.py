import time
from celery_app import celery_app


@celery_app.task(name="ping_task")
def ping_task():
    time.sleep(2)
    return "pong"