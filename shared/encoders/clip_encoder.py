import torch
import open_clip

from shared.encoders.base import BaseEncoder
from shared.encoders.registry import EncoderRegistry

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@EncoderRegistry.register('clip')
class CLIPEncoder(BaseEncoder):

    def __init__(self):
        super().__init__()
        self.model_name = 'ViT-B-16'
        self.pretrained = 'laion400m_e32'
        self.model = open_clip.create_model(
            model_name=self.model_name, pretrained=self.pretrained, device=device
        )
        self.tokenizer = open_clip.get_tokenizer(self.model_name)
    
    def encode_images(self, images):

        with torch.inference_mode():
            
            if isinstance(images, list): images = torch.stack(images)
            image_features = self.model.encode_image(images.to(device))
            image_features /= image_features.norm(dim=-1, keepdim=True)

            return image_features
        
    def encode_texts(self, texts):

        with torch.inference_mode():

            text_features = self.model.encode_text(texts.to(device))
            text_features /= text_features.norm(dim=-1, keepdim=True)

            return text_features
    
    def tokenize(self, texts):
        if not isinstance(texts, list): texts = [texts]
        return self.tokenizer(texts)