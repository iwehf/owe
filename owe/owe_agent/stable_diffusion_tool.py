from langchain.tools import BaseTool
from sd_task.task_runner import run_inference_task
from sd_task.task_args import InferenceTaskArgs
from sd_task.config import Config
from sd_task.cache import MemoryModelCache
import base64
from io import BytesIO

class StableDiffusionTool(BaseTool):
    name: str = "GenerateImage"
    description: str =  (
        "Useful for when you need to generate an image using text prompt."
        "Input: A string as detailed text-2-image prompt describing the image. The string should be created from the user input, should be as detailed as possible, every element in the image, the shape, color, position of the element, the background."
        "Output: the base64 encoded string of the image"
    )
    return_direct: bool = True

    model_cache: MemoryModelCache = None

    def __init__(self):
        super().__init__()
        self.model_cache = MemoryModelCache()

    def _run(self, prompt: str) -> str:

        args = {
            "version": "2.0.0",
            "base_model": "crynux-ai/sdxl-turbo",
            "prompt": prompt,
            "negative_prompt": "",
            "task_config": {
                "num_images": 1,
                "steps": 1,
                "cfg": 0
            },
            "scheduler": {
                "method": "EulerAncestralDiscreteScheduler",
                "args": {
                    "timestep_spacing": "trailing"
                }
            }
        }

        images = run_inference_task(
            InferenceTaskArgs.model_validate(args),
            config=Config.model_validate({
                "deterministic": False,
                "data_dir": {
                    "models": {
                        "huggingface": "models/huggingface",
                        "external": "models/external"
                    }
                }
            }),
            model_cache=self.model_cache
        )
        image = images[0]

        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return "[image]" + base64.b64encode(buffered.getvalue()).decode("utf-8")
