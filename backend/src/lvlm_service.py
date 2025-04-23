import re
import io
import base64
import random
import json

from PIL import Image

from ollama import Client

class LVLMService:

    def __init__(self, host_url: str, model_name: str, max_images: int = 5):
        self.client = Client(host=host_url)
        self.model_name = model_name
        self.max_images = max_images
    
    def _encode_image(self, image_bytes):
        """
        Accepts a BytesIO or raw bytes,
        converts to JPEG for efficiency, and returns base64-encoded string.
        """
        if isinstance(image_bytes, bytes):
            image = Image.open(io.BytesIO(image_bytes))
        elif isinstance(image_bytes, io.BytesIO):
            image_bytes.seek(0)
            image = Image.open(image_bytes)
        else:
            raise ValueError("Unsupported image format for encoding.")

        image = image.resize((256, 256), Image.BILINEAR)

        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=70, optimize=True)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    def _build_prompt(self, num_images):
        
        prompt = (
            "You are shown a set of images that belong to the same visual cluster.\n"
            + "\n".join(["<image>" for _ in range(num_images)]) +
            "\nGenerate a JSON with two fields: 'title' and 'description'.\n"
            "The 'title' should be a concise 2-5 word summary of the visual theme.\n"
            "The 'description' should start with: 'This cluster of images likely shows ...'. "
            "Briefly describe the possible themes, objects, or visual patterns that appear across these images. "
            "Keep the description clear, specific, and concise—just a few sentences at most."
        )

        return prompt
    
    def wrap_in_json(self, raw_content):

        if raw_content.startswith("```"):
            raw_content = re.sub(r"^```(?:json)?\n?", "", raw_content)
            raw_content = re.sub(r"\n?```$", "", raw_content)

        raw_content = raw_content.replace("“", "\"").replace("”", "\"")

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            parsed = {
                "title": "Untitled",
                "description": raw_content
            }
        return parsed
    
    def generate_cluster_content(self, cluster_samples):

        sampled = random.sample(cluster_samples, min(self.max_images, len(cluster_samples)))

        images_encoded = [self._encode_image(sample["image"]) for sample in sampled]

        prompt = self._build_prompt(len(images_encoded))

        response = self.client.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": images_encoded
                }
            ]
        )

        return self.wrap_in_json(
            raw_content=response["message"]["content"].strip()
        )

