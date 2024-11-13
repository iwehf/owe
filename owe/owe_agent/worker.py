import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from dotenv import load_dotenv
load_dotenv("persisted_data/.env")

from .celery import app
from .llm_task import llm
