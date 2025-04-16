class DatasetRegistry:
    _datasets = {}

    @classmethod
    def register(cls, name):
        def inner_wrapper(wrapped_class):
            if name in cls._datasets:
                raise ValueError(f"Dataset '{name}' already exists")
            cls._datasets[name] = wrapped_class
            return wrapped_class
        return inner_wrapper

    @classmethod
    def get_dataset(cls, name, **kwargs):
        if name not in cls._datasets:
            raise ValueError(f"Dataset '{name}' not found")
        return cls._datasets[name](**kwargs)

    @classmethod
    def list_datasets(cls):
        return list(cls._datasets.keys())
