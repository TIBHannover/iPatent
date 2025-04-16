from abc import ABC, abstractmethod

class BaseCluserModel(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def cluster(self, images):
        pass