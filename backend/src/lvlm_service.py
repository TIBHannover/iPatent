import io
import base64
import random

from PIL import Image

from ollama import Client

class LVLMService:

    def __init__(self, host_url: str, model_name: str, max_images: int = 5):
        self.client = Client(host=host_url)
        self.model_name = model_name
        self.max_images = max_images
    
    def _encode_image(self, image):
        """Convert PIL Image to base64 encoded string."""
        if not isinstance(image, Image.Image):
            image = Image.open(image)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    def _build_prompt(self, num_images):
        return (
            "You are shown a set of images that belong to the same visual cluster.\n"
            + "\n".join(["<image>" for _ in range(num_images)]) +
            "\nDescribe the cluster using the following format: 'This cluster shows images ...'. "
            "Briefly explain the key themes, objects, or patterns that appear across these images. "
            "Keep the description clear, specific, and concise—just a few sentences at most."
        )
    
    def generate_cluster_description(self, cluster_samples):

        if not cluster_samples:
            return "No images in this cluster."

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

        return response["message"]["content"].strip()
