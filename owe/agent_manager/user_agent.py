from owe.owe_agent.owe_agent import OweAgent
from owe.telegram.bot import TGBot
from .user_agent_config import UserAgentConfig

class UserAgent:
    def __init__(self, config: UserAgentConfig) -> None:
        self.user_agent_config = config
        self.owe_agent = OweAgent(self.user_agent_config.agent_config)

    def start_tg_bot(self) -> None:
        self.tg_bot = TGBot(self.owe_agent, self.user_agent_config.tg_bot_token, self.user_agent_config.user_id)
        self.tg_bot.start()
