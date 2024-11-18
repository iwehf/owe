import json
from .user_agent_config import UserAgentConfig
from .user_agent import UserAgent
import multiprocessing as mp
import time
import logging
import signal

class AgentManager:
    def __init__(self) -> None:
        self.user_agents = []
        self.user_agent_processes = {}
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.logger = logging.getLogger("[Agent Manager]")

    def load_user_agents(self) -> None:
        with open('persisted_data/agents.json', 'r') as file:
            agents_data = json.load(file)
            self.user_agents = agents_data["agents"]
        self.logger.debug(f"Loaded agents.json. {len(self.user_agents)} agents")

    def start_user_agent(self, user_agent_config: UserAgentConfig):
        user_agent = UserAgent(user_agent_config)
        user_agent.start_tg_bot()

    def exit_gracefully(self, signum, frame):
        self.logger.info("Gracefully shutdown the agent manager in 30 seconds...")
        self.kill_now = True

    def start_agent_process(self, user_agent_config: UserAgentConfig):
        self.logger.info(f"Starting user agent process: {user_agent_config.user_id}")
        p = mp.Process(target=self.start_user_agent, args=(user_agent_config,))
        p.daemon = True
        p.start()
        self.user_agent_processes[user_agent_config.user_id] = p
        self.logger.info(f"User agent process started: {user_agent_config.user_id}")

    def stop_agent_process(self, user_id: str):
        self.logger.info(f"Terminating user agent process: {user_id}")
        p = self.user_agent_processes[user_id]
        p.terminate()
        p.join()
        self.logger.info(f"User agent process terminated: {user_id}")

    def restart_agent_process(self, user_agent_config: UserAgentConfig):
        self.stop_agent_process(user_agent_config.user_id)
        self.start_agent_process(user_agent_config)

    def run(self) -> None:

        self.logger.info("Agent manager starting...")

        self.load_user_agents()

        for user_agent in self.user_agents:
            user_agent["agent_config"]["image_generation_args"]["prompt"] = "placeholder"
            user_agent_config = UserAgentConfig.model_validate(user_agent)
            self.start_agent_process(user_agent_config)

        self.logger.info(f"Started {len(self.user_agents)} user agents.")

        while(not self.kill_now):
            # TODO: Check for config update and restart the agent if necessary
            self.logger.debug("Checking for user agent updates...")
            time.sleep(10)

        self.logger.info("Agent manager terminated!")
