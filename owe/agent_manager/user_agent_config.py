from pydantic import BaseModel
from owe.owe_agent.agent_config import AgentConfig


class UserAgentConfig(BaseModel):
    user_id: str
    tg_bot_token: str
    agent_config: AgentConfig
 