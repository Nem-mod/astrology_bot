from typing import Literal, List

from openai import AsyncOpenAI
from io import BytesIO
from datetime import datetime  # for formatting date returned with images
import base64  # for decoding images if recieved in the reply
from PIL import Image  # pillow, for processing image types


class OpenAIService:
    def __init__(self, api_key: str):
        self._client = AsyncOpenAI(api_key=api_key)

    async def chat_completion(self, query: str, system_prompt: str = None, model: str = "gpt-3.5-turbo-0125",
                              max_tokens: int = 4096, temperature: int = 0, messages=None) -> tuple:
        if messages is None:
            messages = []
        if system_prompt and len(messages) == 0:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})

        response = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            top_p=1,
            temperature=temperature
        )
        res_content = response.choices[-1].message.content
        messages.append(
            {"role": "assistant", "content": res_content}
        )
        return res_content, messages

    async def image_generation(self,
                               prompt: str,
                               model: str = "dall-e-3",
                               size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = "1024x1024",
                               extra_query: str = None,
                               source_dir: str = "./sources"
                               ):

        images_response = await self._client.images.generate(
            model=model,
            n=1,
            size=size,
            prompt=prompt,
            extra_query=extra_query,
            response_format="b64_json"
        )
        images_dt = datetime.utcfromtimestamp(images_response.created)
        img_filename = images_dt.strftime('DALLE-%Y%m%d_%H%M%S')  # like 'DALLE-20231111_144356'
        revised_prompt = images_response.data[0].revised_prompt

        image_data_list = []
        for image in images_response.data:
            image_data_list.append(image.model_dump()["b64_json"])

        # Initialize an empty list to store the Image objects
        image_objects = []
        images_filenames: List[str] = []
        if image_data_list and all(image_data_list):  # if there is b64 data
            # Convert "b64_json" data to png file
            for i, data in enumerate(image_data_list):
                image_objects.append(Image.open(BytesIO(base64.b64decode(data))))  # Append the Image object to the list
                image_objects[i].save(f"{source_dir}/{img_filename}_{i}.png")
                print(f"{img_filename}_{i}.png was saved")
                images_filenames.append(f"{source_dir}/{img_filename}_{i}.png")
        else:
            print("No image data was obtained. Maybe bad code?")

        for image in images:
            try:
                fp = Path(image)
                fp.unlink()
            except Exception as err:
                print(err)


        return images_filenames
