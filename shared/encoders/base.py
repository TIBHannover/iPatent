from abc import ABC, abstractmethod

class BaseEncoder(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def encode_texts(self, texts):
        pass

    @abstractmethod
    def encode_images(self, images):
        pass
