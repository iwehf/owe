from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional, List, Mapping, Any
from .llm_task import llm
import asyncio
import logging
from .agent_config import LLMConfig

class RemoteLLM(LLM):

    @property
    def _llm_type(self) -> str:
        return "remote"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": "remote"}

    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config

    def run_until_complete(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        task = llm.apply_async((self.llm_config, prompt, stop), countdown=5, expires=30)
        resp = ""

        try:
            resp = task.get(timeout=20)
        except Exception as e:
            logging.error(e)

        return resp

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            _: Optional[CallbackManagerForLLMRun] = None
    ) -> str:
        raise Exception("Sync call should never be used")

    async def _acall(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            _: Optional[CallbackManagerForLLMRun] = None
    ) -> str:
        resp = await asyncio.to_thread(self.run_until_complete, prompt, stop)
        return resp
