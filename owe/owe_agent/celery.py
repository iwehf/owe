from celery import Celery
import os

app = Celery(
    'owe_tasks',
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_BACKEND_URL"),
    task_routes={
        "owe.owe_agent.llm_task.llm": {"queue": "llm"},
        "owe.owe_agent.sd_task.sd": {"queue": "sd"}
    })
