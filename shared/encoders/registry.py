class EncoderRegistry:
    _encoders = {}

    @classmethod
    def register(cls, name):
        def inner_wrapper(wrapped_class):
            if name in cls._encoders:
                raise ValueError(f"Encoder '{name}' already exists")
            cls._encoders[name] = wrapped_class
            return wrapped_class
        return inner_wrapper

    @classmethod
    def get_encoder(cls, name):
        if name not in cls._encoders:
            raise ValueError(f"Encoder '{name}' not found")
        return cls._encoders[name]()

    @classmethod
    def list_encoders(cls):
        return list(cls._encoders.keys())
