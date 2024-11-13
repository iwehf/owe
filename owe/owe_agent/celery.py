from celery import Celery
import os

app = Celery('owe_tasks', broker=os.getenv("CELERY_BROKER_URL"), backend=os.getenv("CELERY_BACKEND_URL"))
