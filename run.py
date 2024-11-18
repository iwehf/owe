from dotenv import load_dotenv

load_dotenv("persisted_data/.env")

from owe.agent_manager.agent_manager import AgentManager
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == "__main__":

    logging.info("Owe starting...")

    logging.info("Starting agent manager...")
    AgentManager().run()

    logging.info("Owe stopped!")
