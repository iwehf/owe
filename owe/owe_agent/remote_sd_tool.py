from langchain.tools import BaseTool
from pathlib import Path
from datetime import datetime
import uuid
import asyncio
from .sd_task import sd
import logging
from io import BytesIO
from PIL import Image
import base64
from sd_task.task_args.inference_task.task_args import InferenceTaskArgs

class RemoteSDTool(BaseTool):
    name: str = "GenerateImage"
    description: str =  (
        "Useful for when you need to generate an image using text prompt."
        "Input: A string as detailed text-2-image prompt describing the image. The string should be created from the user input, should be as detailed as possible, every element in the image, the shape, color, position of the element, the background."
        "Output: the base64 encoded string of the image"
    )
    return_direct: bool = True

    task_args: InferenceTaskArgs

    def run_until_complete(self, prompt: str) -> str:

        self.task_args.prompt = prompt

        task = sd.apply_async((self.task_args,), countdown=5, expires=30)
        resp = ""

        try:
            resp = task.get(timeout=20)
        except Exception as e:
            logging.error(e)

        return resp

    def write_image_to_file(self, image_b64:str) -> str:
        image_bytes = base64.b64decode(image_b64.encode("utf-8"))
        image = Image.open(BytesIO(image_bytes))

        image_path = Path("persisted_data") / "images" / datetime.today().strftime('%Y-%m-%d')
        image_path.mkdir(parents=True, exist_ok=True)

        image_id = uuid.uuid4()
        image_filename = image_path / f"{image_id}.jpg"

        image.save(image_filename)

        return image_filename

    async def _arun(self, prompt: str) -> str:
        image_b64 = await asyncio.to_thread(self.run_until_complete, prompt)
        image_filename = await asyncio.to_thread(self.write_image_to_file, image_b64)
        return f"[image]{image_filename}"

    def _run(self, _: str) -> str:
        raise Exception("Sync call should never be used")
