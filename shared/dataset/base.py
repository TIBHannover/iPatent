from abc import ABC, abstractmethod

class BaseDataset(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()