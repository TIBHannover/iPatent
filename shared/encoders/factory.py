from shared.encoders.registry import EncoderRegistry

class EncoderFactory:
    @staticmethod
    def get_encoder(encoder_name):
        return EncoderRegistry.get_encoder(encoder_name)

    @staticmethod
    def list_available_encoders():
        return EncoderRegistry.list_encoders()
