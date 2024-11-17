from pydantic import BaseModel
from sd_task.task_args.inference_task.task_args import InferenceTaskArgs


class LLMConfig(BaseModel):
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.3"
    hf_token: str
    prompt_preset: str = ""


class AgentConfig(BaseModel):
    llm_config: LLMConfig
    image_generation_args: InferenceTaskArgs
