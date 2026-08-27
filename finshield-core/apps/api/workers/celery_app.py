import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))

from celery import Celery

REDIS_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "finshield_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(task_track_started=True)

import tasks  # noqa: E402 -- registers tasks with the app