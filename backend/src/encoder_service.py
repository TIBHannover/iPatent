from shared.encoders.factory import EncoderFactory

from shared.utils.image import preprocess
from shared.utils.common import load_config

config = load_config()

class EncoderService:

    def __init__(self):
        self.encoder = EncoderFactory.get_encoder(
            encoder_name=config['encoder']['name']
        )
    
    def get_encoded_image(self, image):
        return self.encoder.encode_images(
                preprocess(image, tensors=True).unsqueeze(0)
            ).detach().cpu().numpy()

    def get_encoded_text(self, text):
        return self.encoder.encode_texts(
            self.encoder.tokenize(text)
        ).detach().cpu().numpy()